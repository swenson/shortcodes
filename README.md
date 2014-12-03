# shortcodes

This implements URL shortening codes from a random number generator,
written in Python.

For more details on what this code is doing, see [this blog post](http://www.caswenson.com/2014_12_02_so_you_want_to_learn_crypto_part_2_cyclic_groups_and_short_codes).

## Usage

If you have a 1-up counter, you can get back a scrambled short code (5 base32 digits), and recover the counter value from the scrambled code like so:

```
>>> import short_codes
>>> short_codes.short_code(123)
'K8$PN'

>>> short_codes.deshort_code('K8$PN')
123
```

## License

MIT. See [LICENSE](LICENSE).
