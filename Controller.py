
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

