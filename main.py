# Libaries
import pygame
from pathlib import Path
import json
import math

# Setup
pygame.init()
normalMusic = Path("placeholder-normal.ogg").parent / "assets" / "music" / "placeholder-normal.ogg"
try:
    iconImage = pygame.image.load(str(Path("icon.ico")))
    pygame.display.set_icon(iconImage)
except FileNotFoundError:
    print("Falling back to default icon")
screen = pygame.display.set_mode((640, 480))
screenwidth = screen.get_width()
screenheight = screen.get_height()
pygame.display.set_caption("Prealpha")
clock = pygame.time.Clock()
font = pygame.font.SysFont("microsoftsansserif", 30)
debugFont = pygame.font.SysFont("monospace", 20)
pygame.mixer.music.load(str(normalMusic))
pygame.mixer.music.play(-1)

# Variables
isAlive = True
debugMode = False
hitboxSize = 50
playerX = 320  
playerY = 240
playerSpeed = 6
playerAngle = 0
enemyX = 100
enemyY = 100
enemySpeed = 15
enemyBrain = "cooldown"
enemyTargetX = 0
enemyTargetY = 0
enemyTrackingDuration = 30
enemyAttackDuration = 60
enemyCooldownDuration = 15
frames = 0
downtime = 0
frameTarget = enemyTrackingDuration
prevTabKey = False
userdataPath = Path(__file__).parent / "userdata.json"

# Images
backgroundNormalImgPath = Path("ocean1.webp").parent / "assets" / "images" / "ocean1.webp"
backgroundNormalImg = pygame.image.load(str(backgroundNormalImgPath)).convert_alpha()
backgroundNormalImg = pygame.transform.smoothscale(backgroundNormalImg, (screenwidth, screenheight))
carlNormalImgPath = Path("carl normal.webp").parent / "assets" / "images" / "carl" / "carl normal.webp"
carlNormalImg = pygame.image.load(str(carlNormalImgPath)).convert_alpha()
carlNormalImg = pygame.transform.smoothscale(carlNormalImg, (hitboxSize, hitboxSize))

# User Data Shenanigans
try:
    userdata = json.loads(userdataPath.read_text(encoding="utf-8"))
except FileNotFoundError:
    personalBest = 0.0
except json.JSONDecodeError as error:
    print(f"Could not read {userdataPath}: {error}")
    personalBest = 0.0
else:
    savedBest = userdata.get("personal_best") if isinstance(userdata, dict) else None
    if isinstance(savedBest, (int, float)) and not isinstance(savedBest, bool) and math.isfinite(savedBest) and savedBest >= 0:
        personalBest = float(savedBest)
    else:
        print(f"Could not read a valid personal best from {userdataPath}; starting without one.")
        personalBest = 0.0

# Functions
def nextMove(nextBrain):
    global frames, frameTarget, enemyBrain
    if nextBrain == "track":
        frameTarget = frames + enemyTrackingDuration
        enemyBrain = "track"
    elif nextBrain == "attack":
        frameTarget = frames + enemyAttackDuration
        enemyBrain = "attack"
    elif nextBrain == "cooldown":
        frameTarget = frames + enemyCooldownDuration
        enemyBrain = "cooldown"
def enemyMovement():
    global frames, frameTarget, enemyBrain, enemyTargetX, enemyTargetY, enemyX, enemyY
    # Tracking
    if frames < frameTarget and enemyBrain == "track":
        enemyTargetX = playerX
        enemyTargetY = playerY
    elif frames >= frameTarget and enemyBrain == "track":
        nextMove("attack")
        if debugMode:
            print(f"Enemy Target X: {enemyTargetX}")
            print(f"Enemy Target Y: {enemyTargetY}")
    # Attacking
    if frames < frameTarget and enemyBrain == "attack":
        enemyX += (enemyTargetX - enemyX) / enemySpeed
        enemyY += (enemyTargetY - enemyY) / enemySpeed
        if abs((enemyTargetX - enemyX) / enemySpeed) < 0.5 and abs((enemyTargetY - enemyY) / enemySpeed) < 0.5:
            nextMove("cooldown")
            if debugMode:
                print("Reached Target")
    elif (frames >= frameTarget and enemyBrain == "attack"):
        nextMove("cooldown")
        if debugMode:
            print("Timed out")
    # Cooldown
    if frames < frameTarget and enemyBrain == "cooldown":
        pass
    elif frames >= frameTarget and enemyBrain == "cooldown":
        nextMove("track")

def restart(): # Somehow works
    global isAlive, playerX, playerY, playerAngle, enemyX, enemyY, frames, frameTarget, enemyBrain, downtime
    isAlive = True
    playerX = 320
    playerY = 240
    playerAngle = 0
    enemyX = 100
    enemyY = 100
    frames = 0
    frameTarget = enemyTrackingDuration
    enemyBrain = "cooldown"
    downtime = pygame.time.get_ticks()
    pygame.mixer.music.play(-1)

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            print("User closed window")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart()
                print("Game Restarted")
    
    if isAlive:
        # Player Movement
        keys = pygame.key.get_pressed()
        moveX = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        moveY = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        if moveX != 0 or moveY != 0:
            playerAngle = -math.degrees(math.atan2(moveX, -moveY))
            playerAngle += 90
        if keys[pygame.K_LEFT]:
            playerX -= playerSpeed
        if keys[pygame.K_RIGHT]:
            playerX += playerSpeed
        if keys[pygame.K_UP]:
            playerY -= playerSpeed
        if keys[pygame.K_DOWN]:
            playerY += playerSpeed
        if keys[pygame.K_TAB]:
            if not prevTabKey:
                debugMode = not debugMode
        prevTabKey = keys[pygame.K_TAB]

        # Enemy Movement
        enemyMovement()

        ## Boundary Checking
        # Player
        if playerX < 0:
            playerX = 0
        if playerX > 640 - hitboxSize:
            playerX = 640 - hitboxSize
        if playerY < 0:
            playerY = 0
        if playerY > 480 - hitboxSize:
            playerY = 480 - hitboxSize
        # Enemy
        if enemyX < 0:
            enemyX = 0
        if enemyX > 640 - hitboxSize:
            enemyX = 640 - hitboxSize
        if enemyY < 0:
            enemyY = 0
        if enemyY > 480 - hitboxSize:
            enemyY = 480 - hitboxSize

        # Timer calculation
        gametime = ((pygame.time.get_ticks() - downtime) // 100) / 10

        # Frame Drawing
        screen.fill((0, 0, 0))
        screen.blit(backgroundNormalImg, (0, 0))

        # Enemy Drawing
        enemyAppearance = pygame.Surface((hitboxSize, hitboxSize))
        enemyAppearance.fill((255, 0, 0))
        if enemyBrain == "track":
            enemyAppearance.set_alpha(128) # Its fity percent of 255 i think
        else:
            enemyAppearance.set_alpha(255)
        screen.blit(enemyAppearance, (enemyX, enemyY))

        # Hitboxes
        player = pygame.Rect(playerX, playerY, hitboxSize, hitboxSize) # Player (ew stinky)
        enemy = pygame.Rect(enemyX, enemyY, hitboxSize, hitboxSize)  # Collision rect for enemy

        # Player Drawing
        rotatedCarlImg = pygame.transform.rotate(carlNormalImg, playerAngle)
        rotatedCarlRect = rotatedCarlImg.get_rect(center=player.center)
        screen.blit(rotatedCarlImg, rotatedCarlRect)
        
        # Time
        if gametime > personalBest:
            timerColor = (255, 255, 0)
        else:
            timerColor = (255, 255, 255)
        timer = font.render(f"Time: {gametime}", True, timerColor)
        screen.blit(timer, (10, 10))

        # Debug Mode Rendering
        if debugMode:
            debugText = debugFont.render(f"Frame: {frames}\nFrame Target: {frameTarget}\nEnemy Brain: {enemyBrain}\nEnemy Target: ({enemyTargetX}, {enemyTargetY})", True, (255, 255, 255))
            screen.blit(debugText, (10, 40))
            if enemyBrain == "track" or enemyBrain == "attack":
                targetSurface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(targetSurface, (0, 0, 255, 100), (10, 10), 8)
                screen.blit(targetSurface, (enemyTargetX - 10, enemyTargetY - 10)) # Someone explain why theres a -10 here
            # Hitboxes
            # pygame.draw.rect(screen, (0, 255, 0), player)
            # pygame.draw.rect(screen, (255, 0, 0), enemy) 
        
    else:
        # Game over screen
        screen.fill((0, 0, 0))
        gameOverText = font.render("Game Over!", True, (255, 255, 255)) # Bozo died
        timeSurvivedText = font.render(f"Time Survived: {gametime}", True, (255, 255, 255))
        personalBestText = font.render(f"Personal Best: {personalBest}", True, (255, 255, 255))
        restartText = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(gameOverText, (240, 180))
        screen.blit(timeSurvivedText, (screenwidth / 2 - timeSurvivedText.get_width() / 2, 210))
        screen.blit(personalBestText, (screenwidth / 2 - personalBestText.get_width() / 2, 240))
        screen.blit(restartText, (200, 270))
    pygame.display.flip()
    clock.tick(60)
    frames += 1

    # Collision Detection
    if player.colliderect(enemy) and isAlive: # Cat laughing and pointing gif
        isAlive = False
        if gametime > personalBest:
            personalBest = gametime
            userdataPath.write_text(
                json.dumps({"personal_best": personalBest}, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"New personal best: {personalBest}")
        pygame.mixer.music.stop()
        print("Game Over!")

pygame.quit()
# Write personal best even if game closes
if gametime > personalBest:
    personalBest = gametime
    userdataPath.write_text(
        json.dumps({"personal_best": personalBest}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"New personal best: {personalBest}")
