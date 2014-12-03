"""

Use like:

  >>> import short_codes
  >>> short_codes.short_code(123)
  'K8$PN'

  >>> short_codes.deshort_code('K8$PN')
  123

"""

def short_code(i):
  """Return the short code for the 1-up counter i.

  >>> short_code(0)
  'GCWB5'
  >>> short_code(1)
  'CR54K'
  >>> short_code(123)
  'K8$PN'
  """

  return int_to_base32(scramble(i))

def deshort_code(c):
  """Given the short code c, returns the counter value (unscrambled).

  >>> deshort_code('GCWB5')
  0
  >>> deshort_code('CR54K')
  1
  >>> deshort_code('K8$PN')
  123
  """
  return unscramble(base32_to_int(c))

# We use a non-standard base32 alphabet to avoid things like English
# swear words.
base32chars = "BCDFGHJKLMNPQRSTVWXYZ23456789@*$"
base32chars_map = {c: i for i, c in enumerate(base32chars)}

def base32_to_int(s):
  """Converts a base32 string to an integer.

  >>> base32_to_int('BBBBB')
  0
  >>> base32_to_int('BBBBC')
  1
  >>> base32_to_int('CR54K')
  1499879
  """
  nums = [base32chars_map[c.upper()] for c in s]
  return reduce(lambda total, n: total * 32 + n, nums)

def int_to_base32(n):
  """Converts an integer < 32**5 to a 5-character base32 string.

  >>> int_to_base32(0)
  'BBBBB'
  >>> int_to_base32(1)
  'BBBBC'
  >>> int_to_base32(1499879)
  'CR54K'
  """
  return ''.join(base32chars[a] for a in [n / (32*32*32*32),
                  n / (32*32*32) % 32,
                  n / (32*32) % 32,
                  n / (32) % 32,
                  n % 32])

# this is so that 0 won't map to 0, and 1 won't map to 61, etc.
offset = 30

def scramble(x):
  """Scrambles the integer (0 <= x < modulus) by returning g**x (mod modulus).

  >>> scramble(0)
  4244504
  >>> scramble(1)
  1499879
  >>> scramble(123)
  8256874
  """
  return pow(generator, x + offset, modulus)

# Given g**x (mod modulus), returns x
def unscramble(x):
  """Unscrambles the integer (0 <= y < modulus) by computing the discrete logarithm.

  >>> unscramble(4244504)
  0
  >>> unscramble(1499879)
  1
  >>> unscramble(8256874)
  123
  """
  # Use the Pohlig-Hellman algorithm to quickly calculate the discrete logarithm.
  logs = [discrete_log(x, p) for p in p_minus_1_factors]
  num = chinese_remainder_theorem(logs) - offset
  return num % (modulus - 1)

# HERE BE MATHDRAGONS.

# For some background:
#   * http://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm
#   * http://en.wikipedia.org/wiki/Chinese_remainder_theorem

# These parameters are guaranteed to give us the 25-bit short code
# parameters that requires the least RAM to invert.

# Here is Sage code to find the Galois Field with the best order:

#   bestsum = 2^30
#   for p in primes(2^24, 2^25):
#     fsum = 0
#     for f, e in (p - 1).factor():
#       if e != 1:
#           fsum = 2^30
#           break
#       fsum += f
#     if fsum < bestsum:
#       best = p
#       bestsum = fsum
#   print best, best - 1, (best - 1).factor()

#   For the generator, find the smallest prime primitive root of GF(modulus):

#   for q in primes(3, 1000):
#     if GF(modulus)(q).multiplicative_order() == modulus - 1:
#       print q
#       break

generator = 61 # smallest prime primitive root of GF(modulus)
modulus = 17160991 # 25-bit modulus
# 17160991 - 1 = 17160990 = 2 * 3 * 5 * 7 * 11 * 17 * 19 * 23
# this means we'll need to store just 87 discrete logarithms in memory,
# which is about 1 kB including Python overhead
p_minus_1_factors = [2, 3, 5, 7, 11, 17, 19, 23] # factorization of p - 1

def mod_inverse(x, p):
  """Given 0 <= x < p, and p prime, returns y such that x * y % p == 1.

  >>> mod_inverse(2, 5)
  3
  >>> mod_inverse(3, 5)
  2
  >>> mod_inverse(3, 65537)
  21846
  """
  return pow(x, p - 2, p)

# We need the inverses of (modulus - 1) / p for the Chinese Remainder Theorem calculation.
crt_inverses = {p: mod_inverse((modulus - 1) / p, p) for p in p_minus_1_factors}


def chinese_remainder_theorem(nums):
  """Given x = a1 mod n1, x = a2 mod n2, etc., solve for x mod n1*n2*..."""
  s = 0
  for x, n in zip(nums, p_minus_1_factors):
    n_inv = crt_inverses[n]
    s += x * ((modulus - 1) / n) * n_inv
  return s % (modulus - 1)

# Pre-computes all discrete logarithms mod p with generator (modulus - 1) / p.
def calculate_ph_dlog_table(p):
    gx = 1
    g = pow(generator, (modulus - 1) / p, modulus)
    table = {}
    for x in xrange(p):
      table[gx] = x
      gx = (gx * g) % modulus
    return table

pohlig_hellman_dlog_tables = {p: calculate_ph_dlog_table(p) for p in p_minus_1_factors}

# Given g**x mod modulus, returns x mod p.
def discrete_log(x, p):
  y = pow(x, (modulus - 1) / p, modulus)
  return pohlig_hellman_dlog_tables[p][y]

if __name__ == '__main__':
  import doctest
  doctest.testmod()

  # long test:
  for i in xrange(0, modulus - 1):
    assert unscramble(scramble(i)) == i
