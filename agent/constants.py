SECRET_PATTERNS = [
    r'\.env$',
    r'\.env\..+$',
    
    r'\.git/',
    r'\.ssh/',
    r'\.aws/',
    r'\.config/',
    
    r'secrets\.',
    r'secret\.',
    r'password',
    r'credentials',
    r'\.pem$',
    r'\.key$',
    r'\.crt$',
    r'\.p12$',
    r'\.pfx$',
    r'id_rsa',
    r'id_ed25519',
    r'token',
    
    r'\.pytest_cache/',
    r'__pycache__/',
    r'\.mypy_cache/',
    r'\.vscode/',
    r'.*\.log$',
    
    r'database\.(?:sqlite|db|sqlite3)$',
    
    r'\.min\.(?:js|css)$',
]

FILE_COMMANDS = ['explain', 'refactor', 'test', 'docs', 'improve', 'create', 'new', 'write']

PLAN_PROMPT = ''