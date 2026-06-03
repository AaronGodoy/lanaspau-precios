import os

files = [
    r'd:\Python\LanasPau\frontend\src\pages\LoginPage.tsx',
    r'd:\Python\LanasPau\backend\app\core\config.py',
    r'd:\Python\LanasPau\backend\app\utils\seed_data.py',
    r'd:\Python\LanasPau\backend\app\utils\bootstrap.py',
    r'd:\Python\LanasPau\backend\app\schemas\products.py',
    r'd:\Python\LanasPau\backend\app\db\models.py',
    r'd:\Python\LanasPau\frontend\src\services\api.ts',
    r'd:\Python\LanasPau\frontend\src\hooks\useAuth.tsx',
    r'd:\Python\LanasPau\frontend\src\layouts\AppLayout.tsx',
    r'd:\Python\LanasPau\frontend\src\components\Sidebar.tsx',
    r'd:\Python\LanasPau\frontend\src\pages\ReportsPage.tsx',
    r'd:\Python\LanasPau\frontend\index.html'
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Undo the bad PowerShell replacement
    content = content.replace('Lanas Pau Pricing', 'REVERT_1')
    content = content.replace('Lanas Pau.cl', 'REVERT_2')
    content = content.replace('Lanas Pau', 'revesderecho')
    content = content.replace('REVERT_1', 'Lanas Pau Pricing')
    content = content.replace('REVERT_2', 'lanaspau.cl')

    # Now do case-sensitive replacements
    content = content.replace('Revesderecho', 'Lanas Pau')
    content = content.replace('REVESDERECHO', 'LANAS PAU')
    content = content.replace('revesderecho', 'lanaspau')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
