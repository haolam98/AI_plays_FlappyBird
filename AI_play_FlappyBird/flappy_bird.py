import pygame
import neat
import os
import random

pygame.font.init()
# load images and set screen dimension
WIN_WIDTH = 600
WIN_HEIGHT = 800

#-scale2x() double the size of the images, then load the
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))
             ]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))

STAT_FONT = pygame.font.SysFont("comicsans",50)

GEN = 0
#----------------------------------FLAPPY BIRD CLASS----------------------------------
class Bird:
    IMGS= BIRD_IMGS
    MAX_ROTATION = 25 #degree bird going to tilted
    ROT_VEL = 20 #rotation velocity - how much we are going rotate on each frame everytime we miove the bird
    ANIMATION_TIME = 5 #how long to show each bird animation

    def __init__(self,x,y):
        #starting position of the bird
        self.x=x
        self.y=y
        self.tilt =0
        self.tick_count =0
        self.vel = 0
        self.height = self.y
        self.img_count = 0 #img current show
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0 #when we last jump
        self.height = self.y #where the bird jump from

    def move(self):
        self.tick_count +=1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2 #how much we move up/down

        #make sure bird not moving to far up/down
        if d>=16:
            d = 16

        if d<0:
            d -=2

        self.y = self.y + d

        #tilt the bird
        if d<0 or self.y < self.height +50:
            if self.tilt <self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL


    def draw(self,win):
        self.img_count +=1
        if self.img_count <self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 +1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt<=-80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        #rotate image around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL =  5 #move the pipe backward
    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap =100
        self.top = 0
        self.bottom=0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)
        self.PIP_BOTTOM = PIPE_IMG

        #if the bird pass the pipe
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP, (self.x,self.top))
        win.blit(self.PIP_BOTTOM,(self.x, self.bottom))

    def collide(self,bird):
        bird_mask = bird.get_mask()

        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIP_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True #bird collided

        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y= y
        self.x1 = 0
        self.x2= self.WIDTH

    def move(self):
        self.x1-= self.VEL
        self.x2-=self.VEL

        #check if either image is actually offf the screen completely, the nwe cycle it back
        if self.x1 + self.WIDTH <0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH <0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self,win):
        #draw base
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG, (self.x2, self.y))


#----------------------------------***----------------------------------

def draw_window(win,birds,pipes,base,score,gen):
    win.blit(BG_IMG,(0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    text = STAT_FONT.render("Score: "+str(score),1,(255,255,255))
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    pygame.display.update()

def main(genomes,config):

    global GEN
    GEN +=1
    nets =[]
    ge = []
    birds = []

    #set up neuro network for our genome
        # _,g because gnome is a tupple
    for _,g in genomes:
        g.fitness =0 #start with fitness level 0
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,250))
        ge.append(g)
        ge.append(g)

    #run main loop of our game
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0
    clock = pygame.time.Clock()


    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

    run= True
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        #move the bird
        pipe_ind = 0
        if len(birds)>0:
            if len(pipes)>1 and birds[0].x > pipes[0].x +pipes[0].PIPE_TOP.get_width():
                pipe_ind =1
        else:
            #no bird left, quit running the game
            run = False
            break


        for x,bird in enumerate(birds):
            #pass neuro network for bird
            bird.move()
            #add fitness to bird to encourage it moving forward
            ge[x].fitness= ge[x].fitness+0.1
            #activate neural network with the input
                #feed the bird with its height, its distance to bottom + top pipe
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0]>0.5:
                bird.jump()

        #move pipe, base
        rem =[]
        add_pipe = False
        for pipe in pipes:
            for x,bird in enumerate(birds):
                #if bird collide a pipe
                if pipe.collide(bird):
                    ge[x].fitness -=1 #everytime a bird hits pipe, we remove its fitness score
                    # remove the bird
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                #check if bird pass the pipe
                if not pipe.passed and pipe.x<bird.x:
                    #generate new pipe
                    pipe.passed =True
                    add_pipe =True

            # if pipe is off the screen, moving the pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()


        if add_pipe:
            score +=1
            for g in ge:
                g.fitness+=5 #bird get through pipe gain 5 to its fitness score
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
        #if bird hits the ground or bang the top of the screen
            if bird.y+bird.img.get_height() >=730 or bird.y<0:
                #remove bird
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win,birds,pipes,base,score,GEN)



def run(config_file):
    config =neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                               neat.DefaultSpeciesSet,neat.DefaultStagnation,
                               config_file)
    #create population
    p=neat.Population(config)

    #show output report in console
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    #set fitness function: how far the best bird move in the game
    winner = p.run(main,50)

    #show the best bird
    print ('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    #load config file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config-feedfoward.txt')
    run(config_path)
