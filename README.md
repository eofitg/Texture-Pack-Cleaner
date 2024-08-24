# Texture-Pack-Cleaner
Remove files that are the same as **original** or **meaningless** in a custom texture pack.

---
### Size Comparison
- **Before**
![before](./img/before.png)
- **After**
![after](./img/after.png)
---

### TO-DO
- [ ] `asset/minecraft/sounds`
- [ ] More versions (not just 1.8.9)
- [ ] Special files support (not dir and not common file)
- [ ] Custom font support

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
---
