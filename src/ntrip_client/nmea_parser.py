import logging

NMEA_DEFAULT_MAX_LENGTH = 82
NMEA_DEFAULT_MIN_LENGTH = 3
_NMEA_CHECKSUM_SEPERATOR = "*"

class NMEAParser:

    def __init__(self, logerr=logging.error, logwarn=logging.warning, loginfo=logging.info, logdebug=logging.debug):
        # Bit of a strange pattern here, but save the log functions so we can be agnostic of ROS
        self._logerr = logerr
        self._logwarn = logwarn
        self._loginfo = loginfo
        self._logdebug = logdebug

        # Save some other config
        self.nmea_max_length = NMEA_DEFAULT_MAX_LENGTH
        self.nmea_min_length = NMEA_DEFAULT_MIN_LENGTH

    def is_valid_sentence(self, sentence):
        # Simple sanity checks
        if len(sentence) > self.nmea_max_length:
            self._logwarn(f'Received invalid NMEA sentence. Max length is {self.nmea_max_length}, but sentence was {len(sentence)} bytes')
            self._logwarn(f'Sentence: {sentence}')
            return False
        if len(sentence) < self.nmea_min_length:
            self._logwarn(f'Received invalid NMEA sentence. We need at least {self.nmea_min_length} bytes to parse but got {len(sentence)} bytes')
            self._logwarn(f'Sentence: {sentence}')
            return False
        if sentence[0] != '$' and sentence[0] != '!':
            self._logwarn(f'Received invalid NMEA sentence. Sentence should begin with "$" or "!", but instead begins with {sentence[0]}')
            self._logwarn(f'Sentence: {sentence}')
            return False
        if sentence[-2:] != '\r\n':
            self._logwarn(f'Received invalid NMEA sentence. Sentence should end with \\r\\n, but instead ends with {sentence[-2:]}')
            self._logwarn(f'Sentence: {sentence}')
            return False
        if _NMEA_CHECKSUM_SEPERATOR not in sentence:
            self._logwarn(f'Received invalid NMEA sentence. Sentence should have a "{_NMEA_CHECKSUM_SEPERATOR}" character to seperate the checksum, but we could not find it.')
            self._logwarn(f'Sentence: {sentence}')
            return False

        # Checksum check
        data, expected_checksum_str = sentence.rsplit(_NMEA_CHECKSUM_SEPERATOR, 1)
        expected_checksum = int(expected_checksum_str, 16)
        calculated_checksum = 0
        for char in data[1:]:
            calculated_checksum ^= ord(char)
        if expected_checksum != calculated_checksum:
            self._logwarn('Received invalid NMEA sentence. Checksum mismatch');
            self._logwarn(f'Expected Checksum:     0x{expected_checksum:X}')
            self._logwarn(f'Calculated Checksum: 0x{calculated_checksum:X}')
            return False

        # Passed all checks
        return True
