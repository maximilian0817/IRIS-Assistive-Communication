"""IRIS blink-to-Morse timing simulator.

This simulates the timing/decoding logic in the uploaded IRIS Flask backend.
It does not simulate MediaPipe face-landmark detection or a physical camera.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

LETTERS = ['', 'E', 'T', 'I', 'A', 'N', 'M', 'S', 'U', 'R', 'W', 'D', 'K', 'G', 'O',
           'H', 'V', 'F', '', 'L', '', 'P', 'J', 'B', 'X', 'C', 'Y', 'Z', 'Q', '', '']

MORSE_TO_CHAR = {
    '.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I',
    '.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R',
    '...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z'
}
CHAR_TO_MORSE = {v:k for k,v in MORSE_TO_CHAR.items()}


def choose_letter(bits: List[int]) -> str:
    """Mirror the uploaded backend's binary-tree Morse decoder."""
    if len(bits) > 4:
        return 'TOO BIG'
    trace = 1
    for bit in bits:
        if bit == 0:          # dot
            trace = 2 * trace
        else:                 # dash
            trace = 2 * trace + 1
    return LETTERS[int(trace - 1)]


@dataclass
class IrisMorseSimulator:
    dot_limit: float = 0.28
    dash_limit: float = 2.0
    letter_gap: float = 1.0
    bits: List[int] = field(default_factory=list)
    morse: str = ''
    word: str = ''
    event_log: List[Tuple[str, float, str]] = field(default_factory=list)

    def blink(self, duration: float) -> Optional[str]:
        """Process one closed-eye duration using the project thresholds."""
        if duration < self.dot_limit:
            self.bits.append(0)
            self.morse += '.'
            result = 'dot'
        elif duration < self.dash_limit:
            self.bits.append(1)
            self.morse += '-'
            result = 'dash'
        else:
            result = 'ignored'
        self.event_log.append(('blink', duration, result))
        return result

    def idle(self, duration: float) -> Optional[str]:
        """Decode when the no-blink interval reaches the backend's 1 s threshold."""
        decoded = None
        if duration >= self.letter_gap and self.bits:
            decoded = choose_letter(self.bits)
            self.word += decoded
            self.bits.clear()
            self.morse = ''
        self.event_log.append(('idle', duration, decoded or 'no decode'))
        return decoded

    def reset(self):
        self.bits.clear()
        self.morse = ''
        self.word = ''
        self.event_log.clear()

    def encode_text(self, text: str, dot_duration: float = 0.15, dash_duration: float = 0.70,
                    intra_symbol_gap: float = 0.15, letter_gap: float = 1.05) -> str:
        """Feed a synthetic text sequence through the simulator."""
        self.reset()
        for char in text.upper():
            if char == ' ':
                self.word += ' '
                continue
            code = CHAR_TO_MORSE.get(char)
            if not code:
                continue
            for symbol in code:
                self.blink(dot_duration if symbol == '.' else dash_duration)
                self.idle(intra_symbol_gap)
            self.idle(letter_gap)
        return self.word


if __name__ == '__main__':
    sim = IrisMorseSimulator()
    samples = ['SOS', 'HELLO', 'IRIS']
    for sample in samples:
        output = sim.encode_text(sample)
        print(f'{sample:5s} -> {output}')

    print('\nBoundary classification:')
    for d in [0.10, 0.27, 0.28, 0.50, 1.99, 2.00, 2.20]:
        sim.reset()
        print(f'{d:>4.2f} s -> {sim.blink(d)}')
