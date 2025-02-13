"""
CSSE1001 Assignment 3
Semester 2, 2020
"""

__author__ = "{{Noor Naddour}} ({{44885902}})"
__email__ = "n.naddour@uq.edu.au"
__date__ = "07/10/2020"

#importing:
import tkinter as tk
from tkinter import messagebox 
from PIL import Image, ImageTk
from tkinter import filedialog



#Global Constants:
TASK_ONE = 'TASK_ONE' #Blocks Interface
TASK_TWO = 'TASK_TWO' #Illustrated Ibis Game Interface
GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
    "trial57.txt": 4
    #add any appropriate dungeon file name, and max moves
}
PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)
}

WIN_TEXT = "You have won the game with your strength and honour!"
LOSE_TEXT = "You have lost all your strength and honour."
ADVANCED_GAME_WON = "You have finished the level with a score of"
PLAY_AGAIN_Q = "would you like to play again?"

def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout


class Entity(object):
    """
    A generic Entity within the game.
    """
    def __init__(self):
        """Construct an entity with a collision state(bool) and an ID(str)."""
        self._collidable = True
        self._id = 'Entity'

    def get_id(self):
        """(str): Return the Entity's Identification."""
        return self._id
    
    def set_collide(self,collidable):
        """
        Set the collision state of Entity to collidable(bool)

        Parameters:
            collidable(bool): state of collision
        Returns: None
        """
        self._collidable = collidable
        return None 

    def can_collide(self):
        """(bool): Returns Entity's Collision state."""
        return self._collidable
        
    def __str__(self):
        """Returns Entity's string representation"""
        return self.__class__.__name__ + "('{}')".format(self._id)
    
    def __repr__(self):
        """Returns Entity's string representation"""
        return self.__class__.__name__ + "('{}')".format(self._id)

class Wall(Entity):
    """
    Representation of a wall of the dungeon.
    """
    def __init__(self):
        """Construct a wall of the dungeon with a collision state and ID."""
        self._collidable = False
        self._id = WALL

class Item(Entity):
    """
    Abstract representation of an Item the player can interact with.
    """
    def __init__(self):
        """
        Construct an interactable item, with a collision state(bool) and an
        ID(str).
        """
        super().__init__()

    def on_hit(self,game):
        """Raises NotImplementedError

        Parameters:
            game(GameApp<obj>): The current game that is being played.
        """
        raise NotImplementedError()

class Key(Item):
    """
    Representation of a key in the dungeon.
    """
    def __init__(self):
        """
        Construct an interactable/collidable key with a collision state(bool)
            and ID(bool).
        """
        super().__init__()
        self._id = KEY       

    def on_hit(self,game):
        """
        Transfers the key from dungeon to player's inventory when player
            collides with key.

        Parameters:
            game(GameApp<obj>): The current game that is being played.
        """
        player = game.get_player()
        key = game.get_entity(player.get_position())
        player.add_item(key)
        dict1 = game.get_game_information()
        dict1[player.get_position()] = None
        self.set_collide(False)
        return None   
        
class MoveIncrease(Item):
    """
    Representation of an Interactable MoveIncrease item.
    """
    def __init__(self,moves = 5):
        """
        Construct an interactable/collidable MoveIncrease with added
            moves(int), a collision state(bool) and an ID(str).

        Parameters:
            moves(int): Added moves to player's remaining moves. By default
                player's moves increase by 5.
        """
        super().__init__()
        self._id = MOVE_INCREASE
        self._moves = moves

    def get_moves(self):
        """(int): Return the number of increased moves."""
        return self._moves

    def on_hit(self,game):
        """Increases the count of moves of the player upon the player
                collision with MoveIncrease item. This item is removed upon
                collision.

            Paremeters:
                game(GameApp<obj>): The current game that is being played.
        """
        player = game.get_player()
        entity = game.get_entity(player.get_position())
        if isinstance(entity,MoveIncrease):
            move_increase = self.get_moves()
            player.change_move_count(move_increase)

            self.set_collide(False)
            dict1 = game.get_game_information()
            del dict1[player.get_position()]
            return None

class Door(Entity):
    """Representation of the door of the dungeon."""
    def __init__(self):
        """Construct a door in the dungeon with a collision state(bool) and
            an ID(str)
        """
        super().__init__()
        self._id = DOOR
        self._collidable = True

    def on_hit(self,game):
        """Manages player's collision states with Door entity"""
        player = game.get_player()
        inventory = player.get_inventory()
        if any(isinstance(item, Key) for item in inventory):
            game._win = True
            
        else:
            print("You don't have the key!")
        return None

class Player(Entity):
    """Representation of the player in the dungeon."""
    def __init__(self,move_count):
        """
        Construct a player in the dungeon with collision state(bool),
            an ID(str), Inventory(list), position(tuple<int, int>), and move
            count.

        Parameters:
            move_count(int): number of moves a player has to play in dungeon.
        """
        self._id = PLAYER
        self._collidable = True
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self,position):
        """
        Set the position of the player.

        Parameters:
            position(tuple<int, int>): xy position of the player in the dungeon.
        """
        self._position = position
        return None
    
    def get_position(self):
        """(tuple<int, int>): Return the Player's position if it exists."""
        try:
            return self._position
        except NameError:
            return None
        
    def change_move_count(self,number):
        """
        Increases the move count the player can use to move.

        Parameters:
            number(int): the added number of moves to the player's
            remaining moves.
        """
        self._move_count += number
        return None
    
    def moves_remaining(self):
        """(int): Returns the player's remaining move count."""
        return self._move_count
    
    def add_item(self,item):
        """
        Added the item a player collides with from the dungeon
        to their inventory.

        Parameters:
            item(Item<obj>): the item that the player collided with and
            added it to their inventory.
        """
        self._inventory.append(item)
        return None
    
    def get_inventory(self):
        """(list): Returns the player's inventory."""
        return self._inventory

    def set_move_count(self,moves):
        """Sets max number of moves a player has. Used for uploading a game."""
        self._move_count = moves

    def set_inventory(self,inventory):
        """Sets player's inventory a player has. Used for uploading a game."""
        self._inventory = inventory
        
class GameLogic:
    """Contains all the game informaion and how the game should play out."""
    def __init__(self, dungeon_name="game1.txt"):
        """
        Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of game level. By default, it's game1.
        """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False

    def set_dungeon(self, dungeon):
        """Sets the dungeon variable which is a list of lists.
        This method is used in loading a game.

        Parameter:
            dungeon(list of list): Specific dungeon to be played in.
        """
        self._dungeon = dungeon

    def get_dungeon(self):
        """Gets the dungeon which is being played in"""
        return self._dungeon
    
    def get_positions(self, entity):
        """
        Returns a list of tuples containing all positions of a given Entity
             type.

        Parameters:
            entity (str): the id of an entity.

        Returns:
            (list<tuple<int, int>>): Returns a list of tuples representing the 
            positions of a given entity id.
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions
    
    def set_game_information(self):
        """Sets the dictionary of the game to the origianl pre-play one."""
        self._game_information = self.init_game_information()


    def init_game_information(self):
        """(dict): Returns the dictionary containing all positions and
                    all corresponding Entities as the keys and values
                    respectively.
        """
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        
        self._player.set_position(player_pos)

        information = {
            door_position: Door(),
        }

        #if key exists in dungeon, add key to dungeon dictionary.
        for key in key_position:
            information[key] = Key()

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """(Player<obj>): Returns the player object in the game."""
        return self._player

    def get_entity(self, position):
        """
        Given a position, returns entity at that position. If position is
            off-map, it returns None.

        Parameters:
            position(tuple<int, int>): Given position of entity to be found.
        Returns:
            entity(Entity<obj>): Entity object that is in the given position.
                If no entity, returns None
        """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """
        Returns entity in given direction, based on player's position.
            If there is no entity or entity is a Wall, returns None.

        Parameters:
            direction(str): user input for player's next move
            (Up:W, Down:S, Left:A, Right:D)
        Returns:
            entity(Entity<obj>): Entity object that is in player's direction,
            based on player's position.
        """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """(dict): Returns positions and corresponding Entities of the dungeon."""
        return self._game_information

    def get_dungeon_size(self):
        """(int): Returns the dungeon's width."""
        return self._dungeon_size

    def move_player(self, direction):
        """
        Update the player's position in the given direction.

        Parameters:
            direction(str): user input for player's next move
            (Up:W, Down:S, Left:A, Right:D).
        Returns: None
        """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """
        (tuple<int, int>):Returns the new position given the direction.

        Parameters:
            direction(str): user input for player's next move
            (Up:W, Down:S, Left:A, Right:D).
        Returns:
            next_position(tuple<int, int>): the new position of the player given
            the user's inputted direction.
        """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        next_position = (x + dx, y + dy)
        return next_position

    def check_game_over(self):
        """
        Checks if there is no remaining moves for the player.

        Parameters:
            None
        Returns:
            True(bool): if there is no more remaining moves.
            False(bool): otherwise
        """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """
        Sets the game's win state.

        Parameters:
            win(bool): game's win state.
        """
        self._win = win

    def won(self):
        """(bool): Returns game's win state."""
        return self._win

class AbstractGrid(tk.Canvas): #this is an abstract class
    """A generic Grid for the game"""
    def __init__(self,master,rows,cols,width,height,**kwargs):
        """Construct a grid by dividing the given canvas dimensions given
        in pixels (width,heigh) into equal squares of the specified
        number of columns and rows. Assignment 3 assumes #col is equal to
        #rows but width of canvas doesn't necessarily equal its height
        """
        super().__init__(master, width=width,height=height,**kwargs)
        self._master = master
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height
        
        # Cell is one of the rectangles from the grid.
        self._cell_height = height/rows
        self._cell_width = width/cols
        
    def get_bbox(self,position):
        """Calculates the Upper Left vertex and the Lower Right vertex of a rectangle
        given coordinates from the grid (row,col).

        Parameters:
            position(tuple<int, int>): coordinates from the grid where the
                vertices of the box should be specified from.
        Returns:
            bbox(tuple(tuple<int, int>,tuple<int, int>)): A tuple of two tuples
                that specify (row,col) for each of the two vertices we create for the box.
        """ 
        row = position[0]
        col = position [1]

        #Coordinates of the Upper Left corner:
        x1 = col*self._cell_width
        y1 = row*self._cell_height

        #Coordinates of Lower Right corner:
        x3 = (col+1)*self._cell_width
        y3 = (row+1)*self._cell_height

        bbox =((x1,y1),(x3,y3))
        return bbox
    
    def pixel_to_position(self,pixel):
        """Converts (x,y) coordinates in pixels to (row,col) coordinates of the grid.

        Parameters:
            pixel(tuple<int, int>): x and y -coordinates of a pixel on the canvas.

        Return:
            position(tuple<int, int>): row and column -coordinates of the rectangle
                of the grid that includes the specified pixel.
        """
        x,y=pixel
        col_num = x//self._cell_width
        row_num = y//self._cell_height
        
        if col_num <= self._cols and row_num <= self._rows:
            position = (row_num,col_num)
            return position
        else:
            pass
    
    def get_position_center(self,position):
        """Converts (row,col) coordinates of the grid to (x,y) coordinates in
        pixels of the center pixel of the rectangle specified from the grid.

        Parameters:
            position(tuple<int, int>): row and column coordinates of the grid
                rectangle

        Returns:
            pixel(tuple<int, int>): x and y -coordinates for the center pixel
                of the rectangle of the grid.
        """
        row1,col1=position[0],position[1]
        
        pixelx = (col1*self._cell_width)+(1/2*self._cell_width)
        pixely = row1*self._cell_height+(1/2*self._cell_height)
        
        return (pixelx,pixely)
    
    def annotate_position(self,position,text):
        """Writes text in center of a rectangle from the grid.

        Parameters:
            position(tuple<int, int>): row and column coordinates of
                the grid rectangle.
            text(str): the text that needs to appear on the position.

        Return:
            None
        """
        coordinates = self.get_position_center(position)
        self.create_text(coordinates[0],coordinates[1],text=text)
    
    def get_master(self):
        """Gets the tkinter root window of the game."""
        return self._master
    
    def get_rows(self):
        """Gets the number of rows of the grid."""
        return self._rows
    
    def get_cols(self):
        """Gets the number of columns of the grid."""
        return self._cols
    
    def get_width(self):
        """Gets the width of the grid in pixels."""
        return self._width
    
    def get_height(self):
        """Gets the height of the grid in pixels."""
        return self._height
    

    
class DungeonMap(AbstractGrid):
    """The Grid of the Dungeon of the game."""
    def __init__(self,master,size,width=600,**kwargs):
        """Constructs a grid of specified number of rows and cols for the
        dungeon in the game. The dungeon is always a square (heigh = width)
        The grid is always a square (#row = #col).
        """
        rows = size[0]
        cols = size[1]
        height = width
        self._size = size
        super().__init__(master,rows,cols,width,height,**kwargs)
        print('reached here2')

    def draw_grid(self,dungeon,player_position):
        """Draws the dungeon's grid with all illustrations of game's entities.

        Parameters:
            dungeon(GameLogic<obj>): An instance from GameLogic class.
            player_position(tuple<int, int>): player's position in the dungeon.

        Return:
            None
        """
        #clear previous dungeon grid:
        self.delete('all')

        dictionary = dungeon.get_game_information()
        dungeon_size = dungeon.get_dungeon_size()
        entities = [Wall,MoveIncrease,Door,Key]
        annotatable_entities = [MoveIncrease(),Door(),Key()]
        colors = ['Dark grey','Orange','Dark Red','Yellow']
        block_names = ['Banana','Nest','Trash']

        #Drawing Dungeon and Stylising Entities:
        for entity_index,entity_type in enumerate(entities):
            for grid_pos in dictionary.keys():
                if isinstance(dictionary[grid_pos],entities[entity_index]):
                    bbox = self.get_bbox(grid_pos)
                    box_center = self.get_position_center(grid_pos)
                    self.create_rectangle(bbox, fill = colors[entity_index])
                    if any(isinstance(entity,entities[entity_index]) for entity in annotatable_entities):
                        self.annotate_position(grid_pos,block_names[entity_index-1]) 
                            
        #Drawing Player:
        bbox = self.get_bbox(player_position)
        pixel_pos = self.get_position_center(player_position)
        self.create_rectangle(bbox, fill = 'Medium spring green')
        self.annotate_position(player_position,'Ibis')
        
class AdvancedDungeonMap(AbstractGrid):
    """The Grid of the Dungeon of the game."""
    def __init__(self,master,size,width=600,**kwargs):
        """Constructs a grid of specified number of rows and cols for the
        dungeon in the game. The dungeon is always a square (heigh = width)
        The grid is always a square (#row = #col).
        """
        rows = size[0]
        cols = size[1]
        height = width
        self._size = size
        self._image = []
        super().__init__(master,rows,cols,width,height,**kwargs)

    def get_images(self):
        """Saves all images required for dungeon view in a list,
        after appropriate editing.
        """
        #Sizing Ratio:
        sizing_ratio = (int(self._cell_width),int(self._cell_height))

        #Import and resizing images:
        player = Image.open("images\player.png").resize(sizing_ratio)
        wall = Image.open("images\wall.png").resize(sizing_ratio)
        move_increase = Image.open("images\moveIncrease.png").resize(sizing_ratio)
        door = Image.open("images\door.png").resize(sizing_ratio)
        key = Image.open("images\Key.png").resize(sizing_ratio)
        grass = Image.open("images\empty.png").resize(sizing_ratio)

        images = [wall,move_increase,door,key,grass,player]

        for image in images:
            self._image.append(ImageTk.PhotoImage(image))
       
    def draw_grid(self,dungeon,player_position): #this should have some colors in it.
        """Draws the dungeon's grid with all illustrations of game's entities.

        Parameters:
            dungeon(GameLogic<obj>): An instance from GameLogic class.
            player_position(tuple<int, int>): player's position in the dungeon.

        Return:
            None
        """
        #clear previous drawn dungeon grid:
        self.delete('all')
        self.get_images()

        dictionary = dungeon.get_game_information()
        dungeon_size = dungeon.get_dungeon_size()
        entities = [Wall,MoveIncrease,Door,Key]

        #Draw the background grass of the dungeon:
        for row in range(dungeon_size):
            for col in range(dungeon_size):
                position = (row,col)
                pixel_pos = self.get_position_center(position)
                self.create_image(pixel_pos, image=self._image[4])

        #Drawing Dungeon with Entities:
        for entity_index,entity_type in enumerate(entities):
            for grid_pos in dictionary.keys():
                if isinstance(dictionary[grid_pos],entities[entity_index]):
                    bbox = self.get_bbox(grid_pos)
                    box_center = self.get_position_center(grid_pos)
                    self.create_image(box_center, image=self._image[entity_index])
 
        #Drawing Player:
        bbox = self.get_bbox(player_position)
        pixel_pos = self.get_position_center(player_position)
        self.create_image(pixel_pos, image=self._image[5])



class KeyPad(AbstractGrid):
    """Representation of a KeyPad for clicking movement directions."""
    def __init__(self,master,width=200,height = 100,**kwargs):
        """Constructs a Keypad of sepecified width and height"""
        super().__init__(master,rows = 2,cols = 3,width = width,height = height,**kwargs)
        self._master = master
        self._width = width
        self._height = height
        self._direction_names = ["N","W","S","E"]
        self._keypad_pos = [(0,1),(1,0),(1,1),(1,2)]
        self._keyboard_buttons = ['W','A','S','D']
        
        self.draw_keypad()
    def draw_keypad(self):
        """Draws the keypad with text file denoting direction."""
        
        for index,grid_pos in enumerate(self._keypad_pos):
            bbox = self.get_bbox(grid_pos)
            self.create_rectangle(bbox, fill = 'Dark grey')
            self.annotate_position(grid_pos,self._direction_names[index])
        
    def pixel_to_direction(self,pixel):
        """Takes a pixel's x,y coordinates and associates it with a keypad button.

        Parameters:
            pixel(tuple<int, int>): pixel x and y coordinates.

        Returns:
            direction(str): direction in which the player is trying to move.
        """
        position = self.pixel_to_position(pixel)
        for index,tup in enumerate(self._keypad_pos):
            if position == tup:
                direction = self._keyboard_buttons[index]
                return direction

class StatusBar(tk.Frame):
    """Representation of the game's Status"""
    def __init__(self,master,**kwargs):
        """Constructs a Status Bar frame, which includes information
        about remaining moves and time spent playing. It provides options
        to Quit or Replay.
        """
        super().__init__(master,**kwargs)
        self._master = master

        #Prepare Images:
        self._sb_images = []
        self.get_sb_images()

        #Create Buttons, time and moves viewer:
        self.make_buttons()
        self.make_time_view()
        self.make_moves_remaining_view()

    def make_buttons(self):
        """Creates two buttons: New Game and Quit Game."""
        buttons_frame = tk.Frame(self._master)
        buttons_frame.pack(side = tk.LEFT, expand = 1)
        self._new_game_button = tk.Button(buttons_frame, text = "New Game")
        self._new_game_button.pack(side=tk.TOP, expand=1)

        self._quit_button = tk.Button(buttons_frame, text = "Quit")
        self._quit_button.pack(side = tk.TOP, expand=1)
    
    def make_time_view(self):
        """Creates a clock display."""
        timing_frame = tk.Frame(self._master)
        timing_frame.pack(side = tk.LEFT,expand = 1)
        
        self._clock_label = tk.Label(timing_frame)
        self._clock_label.grid()
        
        #specify the orientation of the image,wrt the text.
        self._clock_label["compound"] = tk.LEFT
        self._clock_label["image"] = self._sb_images[0]
        
    def make_moves_remaining_view(self):
        """Creates a display that shows how many moves are remaining
        for the player.
        """
        moves_frame = tk.Frame(self._master)
        moves_frame.pack(side = tk.LEFT, expand = 1)
        self._moves_label = tk.Label(moves_frame)
        self._moves_label.grid()
        #specify the orientation of the image,wrt the text.
        self._moves_label["compound"] = tk.LEFT
        self._moves_label["image"] = self._sb_images[1]

    def set_timer(self,count):
        """Creates a stopwatch for the advanced dungeon game.

        Parameters:
            count(int): the time at which we start the stopwatch.
        Returns:
            count(int): the time increased by increments of seconds.
        """
        if count >=0:
           self._alarm_id = self._master.after(1000, self.set_timer,count+1)
           self._number = f"{count//60}m {count%60}s"
           self._count = count
           string = "Time remaining \n" + self._number
           self._clock_label.config(text = string)
        return count

    def get_sb_images(self):
        """Imports, resizes and stores images needed for Status Bar."""

        clock = Image.open('images\clock.png').resize((40,40))
        lightning = Image.open('images\lightning.png').resize((40,40))

        self._sb_images.append(ImageTk.PhotoImage(clock))
        self._sb_images.append(ImageTk.PhotoImage(lightning))

    def set_quit_button(self,quit_game):
        """Sets the functionality of the Quit Button."""
        self._quit_button.config(command = quit_game)
        
    def set_new_game_button(self,new_game):
        """Sets the functionality of the New Game Button."""
        self._new_game_button.config(command = new_game)

    def set_moves_remaining(self,moves_remaining):
        """Sets the moves_remaining according to game."""
        
        moves_remaining_text = "Moves Left\n" + f'{moves_remaining} moves remaining'
        self._moves_label.config(text = moves_remaining_text)

    def stop_timer(self):
        """Stops Timer in Status Bar"""
        self._master.after_cancel(self._alarm_id)      
        

class GameApp():
    """Communicates between GameLogic and the visual display of the dungeon."""
    def __init__(self,master,task = TASK_ONE,dungeon_name = 'game2.txt'):
        """Constructs a game instance, with its information, dungeon size
                and player. Also, constructs the dungeons display for the game.
        """
        self._master = master
        self._dungeon_name = dungeon_name
        self._task = task
        #Set a title to window:
        self.set_window_title()

        #Set a Label showing game's name:
        self._master.title("Key Cave Adventure Game")
        self._frame = tk.Frame(self._master)
        self._frame.pack(side = tk.TOP)
        

        #Initiate GameLogic instance:
        self._dungeon = GameLogic(self._dungeon_name)
        self._dictionary = self._dungeon.get_game_information()
        self._dungeon_size = self._dungeon.get_dungeon_size()

        
        #Get player info:
        self._player = self._dungeon.get_player()
        self._player_position = self._player.get_position()
        self._moves_remaining = self._dungeon.get_player().moves_remaining()
        self._inventory = self._dungeon.get_player().get_inventory()

        #Initiate Dungeon Map:
        if self._task == TASK_ONE:
            self._dungeon_map = DungeonMap(self._frame, (self._dungeon.get_dungeon_size(), self._dungeon.get_dungeon_size()), 600,bg='light grey')
        elif self._task == TASK_TWO:
            self._dungeon_map = AdvancedDungeonMap(self._frame, (self._dungeon.get_dungeon_size(), self._dungeon.get_dungeon_size()), 600,bg='light grey')
            
        self._dungeon_map.draw_grid(self._dungeon,self._player_position)
        self._dungeon_map.pack(side = tk.LEFT)

        #Initiate KeyPad:
        self._KeyPad = KeyPad(self._frame, 200, 100)
        self._KeyPad.pack(side = tk.LEFT)
        
        #Bind events to commands:
        self._KeyPad.bind("<Button-1>",self.keypad_press)
        self._master.bind("<Key>",self.keyboard_press)
        
        if self._task == TASK_TWO:
            
            self._timer_count = 0

            #Initiate StatusBar:
            self._sb = StatusBar(self._master)
            self._sb.pack(expand = 1,fill = tk.X)
            self._sb.set_quit_button(self.quit)
            self._sb.set_new_game_button(self.play_again)
            self._sb.set_moves_remaining(self._moves_remaining)
            self._sb.set_timer(self._timer_count)

            #Create a Menu Bar:
            self.create_menubar()


    def create_menubar(self):
        """Creates A menubar for saving,loading,restarting and quitting."""
        menubar = tk.Menu(self._master)
        self._master.config(menu = menubar)

        #create the file menu:
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)

        #save load new quit
        file_menu.add_command(label = "Save Game", command = self.save_file)
        file_menu.add_command(label = "Load Game", command = self.load_file)
        file_menu.add_command(label = "New Game", command = self.play_again)
        file_menu.add_command(label = "Quit", command = self.quit)
        self._filename = None


    def set_window_title(self):
        """Sets the title of the window and a framed label of the game's name."""
        label = tk.Label(self._master,text = "Key Cave Adventure Game",bg = 'medium spring green')
        label.config(font=("Calibri",10))
        label.pack(fill=tk.X)
       
    def quit(self):
        """Quit the game."""
        MsgBox = tk.messagebox.askquestion ('Quit Game',f"Are you sure you want to quit?",icon = 'warning')
        if MsgBox == 'yes':
            self._master.destroy()
        else:
            pass
        
    def save_file(self):
        """Saves Game in a file."""
        if self._filename is None:
            filename = filedialog.asksaveasfilename()
            if filename:
                self._filename = filename
        if self._filename:
            dungeon = ""
            # Redraw the dungeon to file:
            for i in range(self._dungeon.get_dungeon_size()):
                rows = ""
                for j in range(self._dungeon.get_dungeon_size()):
                    position = (i,j)
                    entity = self._dungeon.get_game_information().get(position)
                    if entity is not None:
                        char = entity.get_id()
                    elif position == self._dungeon.get_player().get_position():
                        char = PLAYER
                    else:
                        char = " "
                    rows += char
                if i < self._dungeon.get_dungeon_size() - 1:
                    rows += "\n"
                dungeon += rows
            position = self._dungeon.get_player().get_position()
            fd = open(self._filename, 'w')
            fd.write(f"{self._dungeon.get_player().moves_remaining()}")
            fd.write('\n')
            fd.write(str(self._sb._count))
            fd.write('\n')
            fd.write(f"{position}")
            fd.write('\n')
            fd.write(f"{self._inventory}")
            fd.write('\n')
            fd.write(dungeon)
            fd.close()
            
    def load_file(self):
        """Uploads a saved game from a file."""
        filename = filedialog.askopenfilename()
        if filename:
            self._filename = filename
            dungeon_layout = []
            with open(filename, 'r') as file:
                self._load_moves = int(file.readline().strip())
                self._load_time = file.readline()
                file.readline()
                self._load_inventory = file.readline()
                
                for line in file:
                    line = line.strip()
                    dungeon_layout.append(list(line))
                    
            #Load game dictionary:        
            self._dungeon.set_dungeon(dungeon_layout)
            self._dungeon.set_game_information()
            
            #Load player move count:
            self._dungeon.get_player().set_move_count(self._load_moves)
            self._sb.set_moves_remaining(self._load_moves)

            #Load timer:
            self._sb.stop_timer()
            self._sb.set_timer(int(self._load_time))

            #Prepare and Load Inventory:
            #Change string's list representation to a list:
            self._load_inventory =  self._load_inventory.strip('][').split(', ')

            inventory = []
            for key in self._load_inventory:
                inventory.append(Key())
            self._dungeon.get_player().set_inventory(inventory)

            #Redraw dungeon grid:
            self._dungeon_map.draw_grid(self._dungeon,self._dungeon.get_player().get_position())

    def play_again(self):
        """Resets the dungeon to replay."""
        self._dungeon = GameLogic(dungeon_name=self._dungeon_name)
        self._dungeon_map.draw_grid(self._dungeon,self._dungeon.get_player().get_position())
        if self._task == TASK_TWO:
            self._filename = None
            self._moves_remaining = self._dungeon.get_player().moves_remaining()
            self._sb.set_moves_remaining(self._moves_remaining)
            self._sb.stop_timer()
            self._sb.set_timer(0)
            
    def keypad_press(self,event):
        """Interprets user's mouse click on Keypad canvas."""
        pixel = (event.x,event.y)
        direction = self._KeyPad.pixel_to_direction((event.x,event.y))
        self.play(direction)

    def keyboard_press(self,event):
        """Interprets user's keyboard press"""
        direction = event.char
        self.play(direction)
    
    
    def play(self,action):
        """Handles the player's interactions with the game. Decides when the
                game is won/lost
        """
        action = action.lower()
        directions = ['w', 's', 'd', 'a']
        player = self._dungeon.get_player()
        if action in directions:
            direction = action.upper()
            if not self._dungeon.collision_check(direction): #Check if player can travel in direction.
                self._dungeon.move_player(direction)
                self._entity = self._dungeon.get_entity(self._dungeon.get_player().get_position())
                if self._entity is not None:
                    self._entity.on_hit(self._dungeon)
                    
                self._moves_remaining = self._dungeon.get_player().moves_remaining()
                if self._task == TASK_TWO:
                    self._sb.set_moves_remaining(self._moves_remaining-1)
                self._dungeon_map.draw_grid(self._dungeon,self._dungeon.get_player().get_position())

                if self._dungeon.won():
                    if self._task == TASK_ONE:
                        messagebox.showinfo("showinfo", WIN_TEXT)
                    if self._task == TASK_TWO:
                         MsgBox = tk.messagebox.askquestion ('GAME WON',f"{ADVANCED_GAME_WON} {self._sb._number}\n {PLAY_AGAIN_Q}",icon = 'info')
                         if MsgBox == 'yes':
                             self.play_again()
                         else:
                             self._master.destroy()
            else:
                pass
            player.change_move_count(-1)
        else:
            pass
        #check if player lost the game:
        if self._dungeon.check_game_over():
            if self._task == TASK_ONE:
                messagebox.showinfo("showinfo", LOSE_TEXT)
            if self._task == TASK_TWO:
                print(self._sb._number)
                MsgBox = tk.messagebox.askquestion ('GAME LOST',f"{LOSE_TEXT}\n{PLAY_AGAIN_Q}",icon = 'info')
                if MsgBox == 'yes':
                    self.play_again()
                else:
                    self._master.destroy()



            
        
                        
class main():
    master = tk.Tk()
    app = GameApp(master,task = TASK_TWO,dungeon_name = 'game3.txt')
    master.mainloop()
    
    
