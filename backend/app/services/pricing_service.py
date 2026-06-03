from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from app.db.models import CalculatedPrice, PriceSetting, ProductCost, Product

MONEY = Decimal('0.01')

def _d(value: Decimal | float | int | None) -> Decimal:
    return Decimal(str(value or 0))

def to_float(value: Decimal | float | int) -> float:
    return float(_d(value).quantize(MONEY, rounding=ROUND_HALF_UP))

def to_int_money(value: Decimal | float | int) -> float:
    return float(_d(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def round_price(value: Decimal, rule: str) -> Decimal:
    if rule == 'ninguno':
        return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    step = _d(rule)
    if step <= 0:
        return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return (value / step).to_integral_value(rounding=ROUND_HALF_UP) * step

def price_from_margin(costo_total: Decimal, margen: Decimal) -> Decimal:
    divisor = Decimal('1') - (margen / Decimal('100'))
    if divisor <= 0:
        raise ValueError('El margen debe ser menor a 100%.')
    return costo_total / divisor

def calculate_cost_breakdown(valor_compra: float, iva_porcentaje: float, compra_incluye_iva: bool, costo_envio: float = 0, costo_retiro: float = 0, otros_costos: float = 0, costos_fijos_generales: float = 0, cantidad: int = 1) -> dict:
    compra = _d(valor_compra) / _d(cantidad)
    costo_envio = float(_d(costo_envio) / _d(cantidad))
    costo_retiro = float(_d(costo_retiro) / _d(cantidad))
    otros_costos = float(_d(otros_costos) / _d(cantidad))
    iva = _d(iva_porcentaje)
    factor_iva = Decimal('1') + (iva / Decimal('100'))
    if compra_incluye_iva:
        valor_compra_bruto = compra
        valor_compra_neto = compra / factor_iva if factor_iva else compra
        valor_iva = valor_compra_bruto - valor_compra_neto
    else:
        valor_compra_neto = compra
        valor_iva = valor_compra_neto * iva / Decimal('100')
        valor_compra_bruto = valor_compra_neto + valor_iva
    costo_total = valor_compra_bruto + _d(costo_envio) + _d(costo_retiro) + _d(otros_costos) + _d(costos_fijos_generales)
    return {'valor_compra_neto': to_float(valor_compra_neto), 'iva_porcentaje': to_float(iva), 'valor_iva': to_float(valor_iva), 'valor_compra_bruto': to_float(valor_compra_bruto), 'costo_envio': to_float(costo_envio), 'costo_retiro': to_float(costo_retiro), 'otros_costos': to_float(otros_costos), 'costos_fijos_generales': to_float(costos_fijos_generales), 'costo_total': to_float(costo_total)}

def calculate_pricing_from_total(costo_total: float, settings: PriceSetting, manual_margin: float | None = None, override_rounding: str | None = None, product: Product | None = None) -> dict:
    costo = _d(costo_total)
    rounding = override_rounding or settings.redondeo_precio
    
    # Use product specific margins if set, else global settings
    min_margin = product.margen_minimo_porcentaje if product and product.margen_minimo_porcentaje is not None else settings.margen_minimo_porcentaje
    rec_margin = product.margen_recomendado_porcentaje if product and product.margen_recomendado_porcentaje is not None else settings.margen_recomendado_porcentaje
    prem_margin = product.margen_premium_porcentaje if product and product.margen_premium_porcentaje is not None else settings.margen_premium_porcentaje

    minimo = round_price(price_from_margin(costo, _d(min_margin)), rounding)
    recomendado = round_price(price_from_margin(costo, _d(rec_margin)), rounding)
    premium = round_price(price_from_margin(costo, _d(prem_margin)), rounding)
    utilidad = recomendado - costo
    margen_real = (utilidad / recomendado * Decimal('100')) if recomendado else Decimal('0')
    result = {'costo_total': to_float(costo), 'precio_minimo': to_int_money(minimo), 'precio_recomendado': to_int_money(recomendado), 'precio_premium': to_int_money(premium), 'margen_estimado': to_float(margen_real), 'utilidad_estimada': to_float(utilidad)}
    if manual_margin is not None:
        personalizado = round_price(price_from_margin(costo, _d(manual_margin)), rounding)
        utilidad_personalizada = personalizado - costo
        margen_personalizado = (utilidad_personalizada / personalizado * Decimal('100')) if personalizado else Decimal('0')
        result.update({'manual_margin_porcentaje': float(manual_margin), 'precio_personalizado': to_int_money(personalizado), 'utilidad_personalizada': to_float(utilidad_personalizada), 'margen_real_personalizado': to_float(margen_personalizado)})
    else:
        result.update({'manual_margin_porcentaje': None, 'precio_personalizado': None, 'utilidad_personalizada': None, 'margen_real_personalizado': None})
    return result

def build_explanation(costs: dict, settings: PriceSetting, pricing: dict, product: Product | None = None) -> list[str]:
    rec_margin = product.margen_recomendado_porcentaje if product and product.margen_recomendado_porcentaje is not None else settings.margen_recomendado_porcentaje
    return [f"Se parte de un costo neto de compra de CLP {to_int_money(costs['valor_compra_neto'])}.", f"El IVA aplicado es {to_float(costs['iva_porcentaje'])}% y suma CLP {to_int_money(costs['valor_iva'])}.", f"El costo total real queda en CLP {to_int_money(costs['costo_total'])}, incluyendo envio, retiro, otros costos y fijos generales.", f"El precio recomendado usa un margen objetivo de {to_float(rec_margin)}%.", f"El redondeo comercial configurado es a CLP {settings.redondeo_precio}.", f"Con ese criterio, la utilidad estimada es CLP {to_int_money(pricing['utilidad_estimada'])}."]

def create_calculated_price(producto_id: int, costo_total: float, settings: PriceSetting, product: Product | None = None) -> CalculatedPrice:
    pricing = calculate_pricing_from_total(costo_total, settings, product=product)
    return CalculatedPrice(producto_id=producto_id, costo_total=pricing['costo_total'], precio_minimo=pricing['precio_minimo'], precio_recomendado=pricing['precio_recomendado'], precio_premium=pricing['precio_premium'], margen_estimado=pricing['margen_estimado'], utilidad_estimada=pricing['utilidad_estimada'], fecha_calculo=datetime.utcnow())

def create_cost_from_input(payload, settings: PriceSetting, product: Product | None = None) -> tuple[dict, dict]:
    cantidad = getattr(payload, 'cantidad', 1)
    costs = calculate_cost_breakdown(valor_compra=payload.valor_compra, iva_porcentaje=payload.iva_porcentaje or float(settings.iva_porcentaje_default), compra_incluye_iva=payload.compra_incluye_iva, costo_envio=payload.costo_envio, costo_retiro=payload.costo_retiro, otros_costos=payload.otros_costos, costos_fijos_generales=float(settings.costos_fijos_generales), cantidad=cantidad)
    pricing = calculate_pricing_from_total(costo_total=costs['costo_total'], settings=settings, manual_margin=getattr(payload, 'manual_margin_porcentaje', None), override_rounding=getattr(payload, 'redondeo_precio', None), product=product)
    return costs, pricing

def serialize_price_history(price: CalculatedPrice) -> dict:
    return {'id': price.id, 'producto_id': price.producto_id, 'costo_total': to_float(price.costo_total), 'precio_minimo': to_float(price.precio_minimo), 'precio_recomendado': to_float(price.precio_recomendado), 'precio_premium': to_float(price.precio_premium), 'margen_estimado': to_float(price.margen_estimado), 'utilidad_estimada': to_float(price.utilidad_estimada), 'fecha_calculo': price.fecha_calculo}

def serialize_cost(cost: ProductCost) -> dict:
    return {'id': cost.id, 'producto_id': cost.producto_id, 'valor_compra_neto': to_float(cost.valor_compra_neto), 'iva_porcentaje': to_float(cost.iva_porcentaje), 'valor_iva': to_float(cost.valor_iva), 'valor_compra_bruto': to_float(cost.valor_compra_bruto), 'compra_incluye_iva': cost.compra_incluye_iva, 'costo_envio': to_float(cost.costo_envio), 'costo_retiro': to_float(cost.costo_retiro), 'otros_costos': to_float(cost.otros_costos), 'costo_total': to_float(cost.costo_total), 'fecha_compra': cost.fecha_compra}
