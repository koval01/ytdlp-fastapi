import base64


class CustomHasher:
    def __init__(self):
        """Initialize constants and the S-box for non-linear transformation."""
        self.buffer_size = 128
        self.prime1 = 31
        self.prime2 = 37
        self.prime3 = 41
        self.prime4 = 43
        self.sbox = [
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5,
            0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76
        ]

    def custom_hash(self, input_str: str) -> str:
        """
        Hash the input string using custom transformations and permutations.

        :param input_str: The string to hash.
        :return: The first 128 characters of the base64-encoded hash.
        """
        buffer = self._initialize_buffer(input_str)
        self._perform_chaotic_permutations(buffer)
        self._final_permutation(buffer)
        return self._convert_to_base64(buffer)

    def _initialize_buffer(self, input_str: str) -> list:
        """
        Initialize the buffer with prime-based transformations and a dynamic XOR key.

        :param input_str: The input string to initialize the buffer with.
        :return: The initialized buffer.
        """
        buffer = [0] * self.buffer_size
        dynamic_key = self.prime4

        for i in range(len(input_str)):
            buffer[i % self.buffer_size] = (
                buffer[i % self.buffer_size] + ord(input_str[i]) * self.prime1
            ) & 0xFF
            buffer[(i + 1) % self.buffer_size] ^= (
                ord(input_str[i]) * self.prime2
            ) ^ dynamic_key
            buffer[(i + 2) % self.buffer_size] = (
                (buffer[(i + 2) % self.buffer_size] + ord(input_str[i]) * self.prime3)
                & 0xFF
            ) ^ self.sbox[i % len(self.sbox)]
            dynamic_key = (dynamic_key * self.prime2) & 0xFF

        return buffer

    def _perform_chaotic_permutations(self, buffer: list):
        """
        Perform multi-round chaotic permutations on the buffer.

        :param buffer: The buffer to permute.
        """
        for _r in range(3):
            for i in range(len(buffer)):
                # Left rotate
                buffer[i] = (
                    (buffer[i] << (i % 8)) | (buffer[i] >> (8 - (i % 8)))
                ) & 0xFF
                # XOR with dynamic S-box and key
                buffer[i] ^= buffer[(i + self.prime1) % self.buffer_size] ^ self.sbox[
                    (i + self.prime4) % len(self.sbox)
                ]
                buffer[i] = (
                    (buffer[i] + buffer[(i * 5 + _r) % self.buffer_size]) * self.prime1
                ) & 0xFF
            buffer.reverse()  # Reverse buffer for additional permutation

    def _final_permutation(self, buffer: list):
        """
        Apply final permutation and non-linear transformation to the buffer.

        :param buffer: The buffer to transform.
        """
        for i in range(len(buffer)):
            buffer[i] = self.sbox[buffer[i] % len(self.sbox)] ^ buffer[
                (i * 7) % self.buffer_size
            ]
            buffer[i] ^= buffer[(i + self.prime3) % self.buffer_size]

    @staticmethod
    def _convert_to_base64(buffer: list) -> str:
        """
        Convert the buffer to a base64-encoded string.

        :param buffer: The buffer to encode.
        :return: The first 128 characters of the base64-encoded string.
        """
        base64_bytes = base64.b64encode(bytes(buffer))
        base64_str = base64_bytes.decode("utf-8")
        return base64_str[:128]
