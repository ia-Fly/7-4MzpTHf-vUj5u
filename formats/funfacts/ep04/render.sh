cd /home/claude/ff4
export LOCAL_ROOT=/home/claude/ff4/planches
python3 rf2.py http://local/reel.html video out/part1.mp4 27.8 0 417 > out/r1.log 2>&1 &
python3 rf2.py http://local/reel.html video out/part2.mp4 27.8 13.9 834 > out/r2.log 2>&1 &
wait
echo done > out/render.done
