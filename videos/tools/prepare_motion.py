"""Prepare the English UI contract for the recorded motion edition."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    'Inicia sesión con los datos sintéticos de tu fixture.': 'Sign in using your synthetic fixture credentials.',
    'Servicio temporalmente no disponible': 'Service temporarily unavailable',
    'Clave de idempotencia reutilizada': 'Idempotency key reused with different data',
    'Transferencia realizada': 'Transfer completed',
    'Credenciales incorrectas': 'Invalid credentials',
    'Cuenta de pruebas · MXN': 'Test account · MXN',
    'Beneficiario sintético': 'Synthetic beneficiary',
    'Acceso al laboratorio': 'Lab sign in',
    'Nueva transferencia': 'New transfer',
    'Saldo disponible': 'Available balance',
    'Saldo insuficiente': 'Insufficient funds',
    'Importe inválido': 'Invalid amount',
    'Iniciar sesión': 'Sign in',
    'Cuenta origen': 'Source account',
    'Importe (MXN)': 'Amount (MXN)',
    'Beneficiario': 'Beneficiary',
    'Contraseña': 'Password',
    'Usuario': 'Username',
    'Transferir': 'Transfer',
    'lang="es"': 'lang="en"',
}

if __name__ == '__main__':
    count = 0
    for path in (ROOT / 'lab').rglob('*'):
        if any(part in ('evidence', 'node_modules', 'target', '.venv', 'local-results') for part in path.parts):
            continue
        if path.suffix not in ('.html', '.mjs', '.ts', '.py', '.java'):
            continue
        old = path.read_text(encoding='utf-8-sig')
        new = old
        for source, target in REPLACEMENTS.items():
            new = new.replace(source, target)
        if new != old:
            path.write_text(new, encoding='utf-8')
            count += 1
    print(f'Updated {count} UI and test contract files; baseline evidence preserved.')
