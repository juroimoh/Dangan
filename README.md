> this page is a work in progress

# Dangan (弾丸)

Welcome to _Dangan_! In this challenging topdown bullet-hell game, you must defeat all ~~three~~ two (evil) princesses to win.  
Dodge their attacks, fire shots back, and achieve the highest ranks on all levels!

<img width="450" height="316" alt="Dangan Gameplay" src="https://github.com/user-attachments/assets/de54f949-3100-41e1-bb47-6f20520e7da5" />

## Controls

- `↑ ← ↓ →` | Movement and Navigate (alternatively use `WASD`)  
- `SPACE` | Shoot and Select  
- `ESC` | Exit Level/Screen  

There is no mouse functionality.

<img width="450" height="316" alt="Dangan Main Menu" src="https://github.com/user-attachments/assets/a5e2d446-8f52-41c8-8be8-ae3d376089a7" />

## Installation

Make sure your device has Python installed, and your screen has a resolution of at least 900x600.  
This project uses Pygame 2.6.1, and was coded using Python version 3.9. Download Python [here](https://www.python.org/downloads/).  

`1` Click on the green `˂˃ Code` button, then 'Download ZIP'.  
`2` Right click the folder in a File application, and click 'Extract All'.  
Make sure the files are organized as seen in this Repository and below under [Project Files](#project-files).  

`3 Mac/Linux` Open the Terminal on your device and type 'cd ' before dragging the new folder into the Terminal.  
`3 Windows` Open the folder and click on the address bar. Then type 'cmd' and hit Enter.  

`4` Install the required dependencies by running the following command.  
If pip gives an error on Mac or Linux, try using 'pip3 install -r requirements.txt'
```
pip install -r requirements.txt
```

`5` Run the game with the following command.  
If python gives an error on Mac or Linux, try 'python3 dangan.py'
```
python dangan.py
```

## Manual

This section will explain in detail all elements encountered in game, more in depth than the game manual below.  

<img width="450" height="316" alt="Dangan Manual" src="https://github.com/user-attachments/assets/3fa58201-8b11-4655-b0b6-d1a91b74d590" />

**Gameplay**  
You play in a 500x500 pixel box, avoiding projectiles while doing damage to the enemy. Holding down shoot fires bullets rapidly in sets of 3. Each of the bullets can individually do damage to the enemy, so at times it is advantageous to move close to the enemy and shoot.

**Ranks**  
As seen above, you are awarded a rank after surviving a level, namely SHII, KUU, GUTSU, MEI, and HAKU. The first 4 are obtained with an increasing final score (with different thresholds for each level), while HAKU is achieved by taking no damage in a level. 

**Damage**  
You take damage by colliding with the enemy, spinning blades, and bullets. This highlights your player icon red, and blocks you from gaining any score in that time. You also cannot take any damage until you recover from the previous damage. You have 8 lives visualized with 4 hearts, and losing all results in a death. Deaths are not counted as a statistic.

**Graze**  
By narrowly avoiding bullets, you receive bonus points. This can heavily increase your final score. Your graze value is rounded down to the nearest hundredth, and then multiplied by 10, so with a value of 3670 you would get a bonus graze score of 36,000.

**Lore**  
Currently there are two levels, with 3 being planned. You are trying to restore peace by defeating the princesses Sheru (_level 1_), Kiero (_level 2_) and ??? (_level 3_). You cannot 'win' _Dangan_ yet, since not all levels have been made, but a rank of HAKU is considered defeating the princess.

## Project Files

```
Dangan/
├─ assets/
│  ├─ audio/ *
│  │  └─ effects/
│  ├─ entities/
│  ├─ backgrounds/
│  └─ fonts/ *
├─ levels/
├─ LICENSE
├─ README.md
├─ dangan.py
├─ documentation.pdf
└─ requirements.txt
```

`LICENSE`, `README.md`, and `documentation.pdf` are not required to run the game.

---
*All fonts used within `assets/fonts/` belong to their respective creators, and all songs present within the game files `assets/audio/` are property of Ntreev Soft and are not covered by the license.  

_Dangan_  
© 2026 juroimoh
