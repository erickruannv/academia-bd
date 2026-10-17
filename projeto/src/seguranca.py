import base64
import hashlib
import hmac
import secrets

# Formato salvo: pbkdf2_sha256$<iteracoes>$<salt>$<hash>  (cerca de 90 caracteres,
# cabe no VARCHAR(100) da coluna usuarios.senha)
ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600000

def _b64(dados):
    return base64.b64encode(dados).decode("ascii")

def gerar_hash(senha):
    salt = secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)
    return f"{ALGORITMO}${ITERACOES}${_b64(salt)}${_b64(derivada)}"

def verificar_senha(senha, armazenada):
    partes = armazenada.split("$")
    if len(partes) == 4 and partes[0] == ALGORITMO:
        try:
            iteracoes = int(partes[1])
            salt = base64.b64decode(partes[2], validate=True)
            esperado = base64.b64decode(partes[3], validate=True)
        except ValueError:
            return False
        derivada = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, iteracoes)
        return hmac.compare_digest(derivada, esperado)
    # Contas antigas, gravadas em texto puro
    return hmac.compare_digest(senha.encode("utf-8"), armazenada.encode("utf-8"))
