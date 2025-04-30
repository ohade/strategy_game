# Asset Integration Guide

## External Assets

This project can use external assets for better visuals. Here's how to incorporate the free assets from itch.io:

### SpaceShips Pack (https://niko-3d-models.itch.io/free-sc-fi-spaceships-pack)

1. Download the asset pack from: https://niko-3d-models.itch.io/free-sc-fi-spaceships-pack 
2. Extract the downloaded ZIP file
3. From the extracted files, copy the 2D sprite images into the following folders:
   - Copy ship sprites to: `assets/ships/`
   - Rename the appropriate ships to:
     - `friendly_ship.png` (choose a blue/green ship for player units)
     - `enemy_ship.png` (choose a red/orange ship for enemy units)

### Background Assets

For space backgrounds:
1. Download spacey backgrounds from sites like OpenGameArt.org or itch.io
2. Save them in three sizes for the parallax effect:
   - `assets/backgrounds/bg_far.png` (farthest, mostly stars)
   - `assets/backgrounds/bg_mid.png` (middle distance, nebulae)
   - `assets/backgrounds/bg_near.png` (closest, planets/asteroids)

### Effects

For explosion effects and other animations:
1. Look for sprite sheets or animated effects
2. Save individual frames as numbered sequences:
   - `assets/effects/explosion_0.png` through `explosion_4.png`
   - `assets/effects/laser_0.png` through `laser_2.png`

## Asset Dimensions Guidelines

For best results, use these dimensions:
- Ship sprites: 64x64 pixels or 128x128 pixels
- Background layers: 1024x1024 pixels or larger
- Effect animations: 64x64 pixels per frame

The game will automatically scale assets as needed.
