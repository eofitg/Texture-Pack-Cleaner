# Texture-Pack-Cleaner
Remove files that are the same as **original** or **meaningless** in a custom texture pack.

---

### TO-DO
- [ ] `asset/minecraft/sounds`
- [ ] More versions (not just 1.8.9)
- [ ] Special files support (not dir and not common file)

### Usage
- Put your texture packs in `./input/` folder, can be folders or `.zip` files
- Run `./main.py` 
- Check `./output/` folder after seeing 
  ```
  ...
  DONE.
  ```

### Known Bugs 
- `main.py`: `build()` _line 82_
  - Static images with `.mcmeta` files will be also recognized as dynamic images
- `operating_tools.py` `zip_tools.py`
  - Files named with special symbols can not be read correctly. _Which means only empty `.zip` files can be generated for them._

---
