"""Capture actual game-rendered gameplay and synchronized SFX into a trailer.

Run from chuck/chuck with imageio-ffmpeg on PYTHONPATH. No gameplay changes;
shot setup uses checkpoints and inputs use the game's regular movement.
"""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import json, random, subprocess, wave
from collections import deque
import numpy as np
import pygame
import imageio_ffmpeg
from src.core.game import Game
from src.core import config
from src.world.transitions import AREA_WALK_EXITS

OUT = ROOT.parents[1] / 'artifacts' / 'trailer'
FPS = 30
SHOTS = [('waterdeep_start', 5), ('waterdeep_plaza_from_docks', 8),
         ('sewer_entrance', 3), ('chult_falls', 5),
         ('temple_1', 5), ('temple_2', 5), ('ship_exterior_deck', 5),
         ('feywild_2', 5), ('modern_city_1', 5)]


def route(world, steps=30):
    start = world._player_tile()
    q = deque([start]); parent = {start: None}; depth = {start: 0}
    forbidden = {'V', 's', '♠', '≋'}
    forbidden.update(char for (name, char) in AREA_WALK_EXITS if name == world.map_name)
    while q:
        tile = q.popleft()
        if depth[tile] >= steps:
            continue
        for dx, dy in ((1,0),(0,-1),(0,1),(-1,0)):
            nxt = tile[0]+dx, tile[1]+dy
            if nxt in parent or world.tilemap.is_solid(*nxt): continue
            if world.tilemap.terrain_at(*nxt) in forbidden: continue
            parent[nxt] = tile; depth[nxt] = depth[tile]+1; q.append(nxt)
    end = max(depth, key=lambda t: (depth[t], t[0]))
    path = []
    while end is not None:
        path.append(end); end = parent[end]
    return list(reversed(path))


def read_wav(path):
    with wave.open(str(path)) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32)/32768
        return data.reshape(-1,w.getnchannels()).mean(axis=1), w.getframerate()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    random.seed(12)
    game = Game(save_path=OUT/'capture-settings.json')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    video = OUT/'picture.mp4'
    cmd = [ffmpeg,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
           '-s','320x180','-r',str(FPS),'-i','-','-an','-vf','scale=1920:1080:flags=neighbor',
           '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(video)]
    encoder = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    frame = pygame.Surface((320,180)); clock = [0.0]; effects=[]; manifest=[]
    game.audio.play_sfx = lambda name: effects.append((clock[0],name))
    music_events=[]
    def record_music(filename, loop=True):
        if music_events and music_events[-1][1:3] == (filename, loop):
            return
        music_events.append((clock[0],filename,loop,game.audio.volume_for(filename)))
    game.audio.play_music = record_music
    def emit():
        encoder.stdin.write(pygame.image.tobytes(frame,'RGB'))
        clock[0]+=1/FPS
    try:
        for index,(checkpoint,seconds) in enumerate(SHOTS):
            world=game.checkpoints.load_checkpoint(checkpoint)
            assert not any(s in world.map_name for s in ('tahuya','cabin','desert_trio'))
            world._arrival_fade_t=None
            subject=None
            npc=None
            dialogue_frames=0
            dialogue_lines=[]
            if checkpoint=='waterdeep_plaza_from_docks':
                npc=next(n for n in world.npcs if n.dialogue_id=='blacksmith')
                world.player.x=npc.x+npc.width/2-world.player.width/2
                world.player.y=npc.y+npc.height+28
                world.player.facing='up'
                world.camera.follow(world.player)
            before_cigarettes=game.cigarettes.total
            before_enemies=len(world.rats)
            if checkpoint in ('waterdeep_start','temple_1','sewer_entrance'):
                objects=world.rats if checkpoint=='sewer_entrance' else world.breakables
                subjects=[o for o in objects
                          if not world.tilemap.is_solid(int((o.x+o.width/2)//16),int((o.y+o.height/2+24)//16))]
                subject=subjects[0]
                if checkpoint=='sewer_entrance':
                    subject=next(r for r in world.rats if r.patrolling)
                world.player.x=subject.x+subject.width/2-world.player.width/2
                world.player.y=subject.y+subject.height/2+24-world.player.height/2
                world.player.facing='up'
                if checkpoint=='sewer_entrance':
                    world.player.x=subject.x+subject.width/2-14-world.player.width/2
                    world.player.y=subject.y+subject.height/2-world.player.height/2
                    world.player.facing='right'
                world.camera.follow(world.player)
            if checkpoint=='temple_2':
                world.player.x=23.5*16-world.player.width/2
                world.player.y=32.5*16-world.player.height/2
                world.player.facing='up'
                world.camera.follow(world.player)
            if checkpoint == 'temple_9':
                # Advance the entrance conversation before this action take.
                effect_start=len(effects)
                for _ in range(80):
                    game.input.begin_frame()
                    game.input._actions_down=set()
                    game.input._actions_just_pressed.add('interact')
                    game.scenes.update(1/FPS)
                del effects[effect_start:]
                cx,cy=world._battle_establishing_focus()
                candidates=[(x,y) for x in range(int(cx//16)-6,int(cx//16))
                            for y in range(int(cy//16)-2,int(cy//16)+3)
                            if not world.tilemap.is_solid(x,y)
                            and world.tilemap.terrain_at(x,y) not in {'V','s','♠','≋'}]
                tx,ty=min(candidates,key=lambda t: abs(t[0]-(cx//16-4))+abs(t[1]-cy//16))
                world.player.x=(tx+.5)*16-world.player.width/2
                world.player.y=(ty+.5)*16-world.player.height/2
                world.camera.follow(world.player)
            path=route(world,int(seconds*5)); target=1
            start=clock[0]; positions=[]
            for n in range(seconds*FPS):
                game.input.begin_frame()
                actions=set()
                if target<len(path):
                    tx,ty=path[target]; px=(tx+.5)*16-world.player.width/2; py=(ty+.5)*16-world.player.height/2
                    dx,dy=px-world.player.x,py-world.player.y
                    if abs(dx)<2 and abs(dy)<2: target+=1
                    elif abs(dx)>2: actions.add('move_right' if dx>0 else 'move_left')
                    elif abs(dy)>2: actions.add('move_down' if dy>0 else 'move_up')
                game.input._actions_down=actions
                if npc is not None:
                    game.input._actions_down={'move_up'} if 12<=n<21 else set()
                    if n in (28,190): game.input._actions_just_pressed.add('interact')
                    if n>205: game.input._actions_down={'move_right'}
                if subject is not None:
                    actions=set()
                    if checkpoint=='sewer_entrance':
                        if subject.alive and n>4:
                            dx=subject.x+subject.width/2-world.player.hitbox.centerx
                            dy=subject.y+subject.height/2-world.player.hitbox.centery
                            if abs(dx)>abs(dy):
                                world.player.facing='right' if dx>0 else 'left'
                            else: world.player.facing='down' if dy>0 else 'up'
                            if max(abs(dx),abs(dy))>16:
                                actions.add('move_'+world.player.facing)
                            elif n%8==0: game.input._actions_just_pressed.add('scratch')
                    else:
                        if 18<n<28: actions.add('move_up')
                        if n in (30,42,54): game.input._actions_just_pressed.add('scratch')
                        if 64<n<80: actions.add('move_up')
                        if 110<n<150: actions.add('move_right')
                    game.input._actions_down=actions
                if checkpoint=='temple_2':
                    world.player.facing='up'
                    cy=world.player.hitbox.centery/16
                    game.input._actions_down={'move_up'} if n>15 and cy>16.5 else set()
                    if not world.player.jumping and any(1.0<cy-row<1.4 for row in (30,24,18,12,6)):
                        game.input._actions_just_pressed.add('jump')
                if n in (65,125) and checkpoint in ('chult_falls','feywild_2'):
                    game.input._actions_just_pressed.add('jump')
                game.scenes.update(1/FPS)
                if npc is not None and game.scenes.current is not world:
                    dialogue_frames+=1
                    dialogue_lines=list(getattr(game.scenes.current,'_lines',[]))
                frame.fill((0,0,0)); game.scenes.draw(frame)
                if n==seconds*FPS//2: pygame.image.save(frame,OUT/f'shot-{index+1}.png')
                positions.append((round(world.player.x,1),round(world.player.y,1)))
                emit()
            manifest.append(dict(checkpoint=checkpoint,map=world.map_name,start=start,seconds=seconds,
                                 distinct_positions=len(set(positions)),path_tiles=len(path),
                                 cigarettes_collected=game.cigarettes.total-before_cigarettes,
                                 enemies_defeated=before_enemies-len(world.rats),
                                 object_broken=subject is not None and not getattr(subject,'intact',True),
                                 npc_dialogue=dialogue_lines,dialogue_frames=dialogue_frames,
                                 end_tile=world._player_tile()))
            print(manifest[-1],flush=True)
        encoder.stdin.close(); assert encoder.wait()==0
    finally:
        game._shutdown()
    rate=22050; length=round(clock[0]*rate)
    mixed=np.zeros(length,dtype=np.float32)
    for index,(at,filename,loop,volume) in enumerate(music_events):
        end=music_events[index+1][0] if index+1<len(music_events) else clock[0]
        left,right=round(at*rate),round(end*rate)
        music,sr=read_wav(config.MUSIC_DIR/filename); assert sr==rate
        count=right-left
        if count<=0: continue
        segment=np.resize(music,count) if loop else np.pad(music,(0,max(0,count-len(music))))[:count]
        # Tiny edge ramps prevent clicks at edits without overlapping worlds.
        ramp=min(220,count//2)
        segment=segment.copy()
        segment[:ramp]*=np.linspace(0,1,ramp)
        segment[-ramp:]*=np.linspace(1,0,ramp)
        mixed[left:right]=segment*volume
    for at,name in effects:
        path=config.SFX_DIR/f'{name}.wav'
        if not path.exists(): continue
        sound,sr=read_wav(path); assert sr==rate
        i=round(at*rate); count=min(len(sound),length-i)
        if count>0: mixed[i:i+count]+=sound[:count]*.65
    mixed*=min(1,.94/max(.01,float(np.max(np.abs(mixed)))))
    with wave.open(str(OUT/'soundtrack.wav'),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes((mixed*32767).astype('<i2').tobytes())
    subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(video),'-i',str(OUT/'soundtrack.wav'),
                    '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',
                    str(OUT/'CHUCK-gameplay-trailer.mp4')],check=True)
    (OUT/'shots.json').write_text(json.dumps(dict(duration=clock[0],shots=manifest,sfx_events=effects,music_events=music_events),indent=2))
    print('TRAILER COMPLETE',flush=True)

if __name__=='__main__': main()
