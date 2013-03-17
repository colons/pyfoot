from os import urandom
from binascii import hexlify, unhexlify
from pbkdf2 import PBKDF2


class Authenticator():
    """ PBKDF2 authenticator module
    Uses https://github.com/dlitz/python-pbkdf2
    """

    def __init__(self, key_length=32, salt_length=32, iterations=10000,
                 key_hash='sha256'):
        """ key_length and salt_length are in bytes
        iterations is the number of iterations used with PBKDF2
        key_hash is any of the hash algorithms provided by hashlib
        """

        exec('from hashlib import ' + key_hash)
        self.key_hash = locals()[key_hash]
        self.key_length = key_length
        self.salt_length = salt_length
        self.iterations = iterations

    def check_passkey(self, passkey, password):
        """
        Take a passkey string (PBKDF2 hexkey of password + hex of salt) and a
        plaintext password and return the truth of their equivalency.
        """

        key = passkey[:self.key_length*2]
        salt = unhexlify(passkey[
            self.key_length*2:self.key_length*2 + self.salt_length*2
        ].encode('us-ascii'))
        gen_key = PBKDF2(password, salt, iterations=self.iterations,
                         digestmodule=self.key_hash).hexread(self.key_length)
        return gen_key == key

    def make_passkey(self, password):
        """
        Take a plaintext password and return a generated passkey string.
        """

        gen_salt = urandom(self.salt_length)
        gen_key = PBKDF2(password, gen_salt, iterations=self.iterations,
                         digestmodule=self.key_hash).hexread(self.key_length)
        return gen_key + hexlify(gen_salt).decode('us-ascii')
