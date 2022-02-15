# Bomberman pygame application day 2

- Read [the guideline](https://github.com/mate-academy/py-task-guideline/blob/main/README.md) before start
- [Pygame primer](https://realpython.com/pygame-a-primer/#sprite-groups)
- [Pygame sprites and groups](https://kidscancode.org/blog/2016/08/pygame_1-2_working-with-sprites/)

You already have spyder enemies that charge the player, 
bombs that can explode and kill enemies and the player.
Now you have to implement such features:
1. Create an Enemy class hierarchy and add other types of enemies, for example:
    1. Boar that can drop rocks, all units cannot walk over the rocks, but
   rocks can be destroyed by bombs.
    2. Bird that don't charge the player, can fly over the obstacles, can
   drop bombs.
2. Create an Effect class hierarchy. After an eny enemy dies, it has a 
small chance for a random effect to be dropped. Effect changes the
characteristics of the player if the player picks it up. Create a few types
of effects, for example:
    1. Effect that heals player for 20 health points.
    2. Effect that slows player for 2 speed point.
    3. Effect that accelerates player for 2 speed point.
   