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
