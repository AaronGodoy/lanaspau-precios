export type Role = 'administrador' | 'usuario';

export interface User {
  id: number;
  nombre: string;
  email: string;
  rol: Role;
  activo: boolean;
  fecha_creacion: string;
}

export interface Product {
  id: number;
  codigo_producto: string;
  nombre: string;
  marca?: string | null;
  categoria?: string | null;
  color?: string | null;
  gramaje?: string | null;
  metros?: number | null;
  proveedor_id?: number;
  proveedor_rel?: { id: number; nombre: string; };
  descripcion?: string | null;
  stock: number;
  stock_minimo?: number;
  costo_inicial_total?: number;
  compra_incluye_iva?: boolean;
  margen_minimo_porcentaje?: number | null;
  margen_recomendado_porcentaje?: number | null;
  margen_premium_porcentaje?: number | null;
  activo: boolean;
  fecha_creacion: string;
  latest_cost_total?: number | null;
  latest_recommended_price?: number | null;
}

export interface DashboardItem {
  producto_id: number;
  codigo_producto: string;
  nombre: string;
  categoria?: string | null;
  costo_total?: number | null;
  precio_recomendado?: number | null;
  margen_estimado?: number | null;
  fecha?: string | null;
}

export interface DashboardData {
  total_productos: number;
  promedio_margen: number;
  total_invertido_inventario: number;
  valor_potencial_venta: number;
  productos_mejor_margen: DashboardItem[];
  productos_menor_margen: DashboardItem[];
  ultimos_productos: DashboardItem[];
}

export interface SettingsData {
  id: number;
  margen_minimo_porcentaje: number;
  margen_recomendado_porcentaje: number;
  margen_premium_porcentaje: number;
  iva_porcentaje_default: number;
  redondeo_precio: 'ninguno' | '100' | '500' | '1000';
  moneda: string;
  costos_fijos_generales: number;
}

export interface CalculationResult {
  producto_id?: number | null;
  valor_compra_neto: number;
  iva_porcentaje: number;
  valor_iva: number;
  valor_compra_bruto: number;
  costo_total: number;
  precio_minimo: number;
  precio_recomendado: number;
  precio_premium: number;
  margen_estimado: number;
  utilidad_estimada: number;
  manual_margin_porcentaje?: number | null;
  precio_personalizado?: number | null;
  utilidad_personalizada?: number | null;
  margen_real_personalizado?: number | null;
  explicacion: string[];
  fecha_calculo?: string | null;
}
