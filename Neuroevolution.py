import pygame
from pygame.locals import *
from random import randint, uniform, random
from copy import deepcopy
from sys import exit
pygame.init()


pygame.key.set_repeat(500, 50)

class screen():


    def __init__(self, Width, Height, FPS, Speed, Images):
        self.Width = Width
        self.Height = Height
        self.FPS = FPS
        self.Display = pygame.display.set_mode((self.Width, self.Height))
        pygame.display.set_caption('Flappy Bird!')
        self.Clock = pygame.time.Clock()

        self.Top = pygame.transform.scale(pygame.image.load(Images['Top']), (640, 350))
        self.Bottom = pygame.image.load(Images['Bottom'])
        self.OtherBottom = pygame.image.load(Images['Bottom'])

        self.x = 0
        self.Otherx = 640

        self.Speed = Speed


    def Move(self):
        self.x -= self.Speed
        self.Otherx -= self.Speed
        if self.Otherx < -640:
            self.Otherx = 400
        if self.x < -640:
            self.x = 400


    def Update(self):
        self.Display.blit(self.Bottom, (self.x, 350))
        self.Display.blit(self.OtherBottom, (self.Otherx, 350))


        Game.ShowScore(Game.Score)
        Game.ShowHighScore()
        Game.ShowGeneration(Population.Generation)
        Game.ShowFPS(self.FPS)
        Game.ShowNumberAlive(len(Population.Population))
        Game.ShowPopulationSize()


        self.Clock.tick(self.FPS)
        pygame.display.update()
        self.Display.blit(self.Top, (0, 0))




class bird():


    def __init__(self, y, velocity, gravity, falling_increase, HitBoxWidth, HitBoxHeight, x_Offset, y_Offset, Image):
        self.START_Velocity = velocity
        self.Velocity = velocity
        self.Gravity = gravity
        self.x = Screen.Width // 2
        self.y = y
        self.FallingIncrease = falling_increase
        self.Falling = 1

        self.Color = Color

        self.HitBoxWidth = HitBoxWidth
        self.HitBoxHeight = HitBoxHeight

        self.HitBox = pygame.Rect(self.x + x_Offset, self.y + y_Offset, self.HitBoxWidth, self.HitBoxHeight)


        self.Image = pygame.image.load(Image)


        self.x_Offset = x_Offset
        self.y_Offset = y_Offset

        self.Fitness     = 0
        self.Probability = 0


        self.Brain = neuralNetwork(6, 10, 1)


    def Draw(self):
        Screen.Display.blit(self.Image, (self.HitBox[0] - self.x_Offset, self.HitBox[1] - self.y_Offset))
        # pygame.draw.rect(Screen.Display, (255, 0, 0), self.HitBox, 1)


    def Jump(self):
        self.Velocity = 10
        self.Falling = 1


    def Update(self):
        self.y -= self.Velocity
        self.Velocity *= self.Gravity
        self.y += self.START_Velocity - self.Velocity + self.Falling
        self.Falling *= self.FallingIncrease
        self.HitBox = pygame.Rect(self.x + self.x_Offset, self.y + self.y_Offset, self.HitBoxWidth, self.HitBoxHeight)


    def Collision(self):
        if self.HitBox.colliderect(Game.Pipe.BottomHitBox) or self.HitBox.colliderect(Game.Pipe.TopHitBox) or self.y < -10 or self.y >= Screen.Height - self.HitBoxHeight - (Screen.Height - 350):
            return True
        return False




class pipe():


    def __init__(self, Height, x_Offset, y_Offset, Images):
        self.Height = Height
        self.Images = Images
        self.x = 400

        self.x_Offset = x_Offset
        self.y_Offset = y_Offset

        self.Bottom = pygame.transform.scale(pygame.image.load(Images['Bottom']), (350, 500))
        self.Top = pygame.transform.scale(pygame.image.load(Images['Top']), (350, 500))


    def Update(self):
        self.x -= 2
        self.BottomHeight = Screen.Height - self.Height
        self.TopHeight = Screen.Height - self.Height - 150 - 500
        self.BottomHitBox = pygame.Rect(self.x, self.BottomHeight, 72, 500)
        self.TopHitBox = pygame.Rect(self.x, self.TopHeight, 72, 500 - 10)


    def Draw(self):
        Screen.Display.blit(self.Bottom, (self.BottomHitBox[0] - self.x_Offset, self.BottomHitBox[1] - self.y_Offset))
        Screen.Display.blit(self.Top, (self.TopHitBox[0] - self.x_Offset, self.TopHitBox[1] - self.y_Offset))




class game():


    def __init__(self):
        self.Jump = False
        self.Pipe = pipe(randint(10, 20) * 10, 3, 5, {'Bottom': 'BottomPipe.png', 'Top': 'TopPipe.png'})

        self.ScoreFont       = pygame.font.SysFont('Impact', 30, False, False)
        self.HighScoreFont   = pygame.font.SysFont('Impact', 20, False, False)
        self.GenerationFont  = pygame.font.SysFont('Impact', 40, False, False)
        self.FPSFont         = pygame.font.SysFont('Impact', 15, False, False)
        self.NumberAliveFont = pygame.font.SysFont('Impact', 20, False, False)

        self.ScoreColor       = (255, 255, 255)
        self.HighScoreColor   = (255, 255, 255)
        self.GenerationColor  = (255,   0,   0)
        self.FPSColor         = (  0,   0,   0)
        self.NumberAliveColor = (  0,   0,   0)


        self.CanScore = True
        self.Score = 0

        self.HighScore = 0
        self.HighestGeneration = 1


    def Terminate(self):
        pygame.quit()
        exit()


    def SaveHighScore(self):
        self.File = open("HighScore.txt", 'r')
        self.AllTimeHigh = self.File.read()
        self.File.close()
        self.AllTimeHigh = int(self.AllTimeHigh.split(": ")[1])
        if self.HighScore > self.AllTimeHigh:
            self.File = open("HighScore.txt", 'w')
            self.File.write("High Score: " + str(self.HighScore))
            self.File.close()


    def Inputs(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_s:
                    File = open('BestBird.Data', 'w')
                    File.truncate()

                    BirdBrain = Population.Population[0].Brain
                    for Thing in BirdBrain.Weights:
                        File.write(str(Thing.Data))

                    File.close()
                    print('Data saved.')


                if event.key == K_ESCAPE:
                    self.Length = len(Population.Population)

                    for index, _ in enumerate(Population.Population[::-1]):
                        Population.PossibleParents.insert(0, Population.Population.pop(self.Length - index - 1))


                if event.key == K_UP:
                    Screen.FPS += 1
                if event.key == K_DOWN:
                    Screen.FPS -= 1
                if event.key == K_SPACE:
                    Screen.FPS = 0


            if event.type == QUIT:
                self.Terminate()


    def ShowScore(self, Score):
        self.ScoreText = self.ScoreFont.render('Score: ' + str(Score), True, self.ScoreColor, None)
        Screen.Display.blit(self.ScoreText, (10, 5))


    def ShowHighScore(self):
        self.HighScoreText = self.HighScoreFont.render('High Score: ' + str(self.HighScore) + ', Generation: ' + str(self.HighestGeneration), True, self.HighScoreColor, None)
        Screen.Display.blit(self.HighScoreText, (10, 35))


    def ShowGeneration(self, Generation):
        self.GenerationText = self.GenerationFont.render('Generation: ' + str(Generation), True, self.GenerationColor, None)
        Screen.Display.blit(self.GenerationText, (5, 348))


    def ShowFPS(self, FPS):
        if FPS:
            self.FPSText = self.FPSFont.render('FPS: ' + str(FPS), True, self.FPSColor, None)
        else:
            self.FPSText = self.FPSFont.render('FPS: MAX', True, self.FPSColor, None)
        Screen.Display.blit(self.FPSText, (345, 380))


    def ShowNumberAlive(self, NumberAlive):
        self.NumberAliveText = self.NumberAliveFont.render('Number Alive: ' + str(NumberAlive), True, self.NumberAliveColor, None)
        Screen.Display.blit(self.NumberAliveText, (250, 25))


    def ShowPopulationSize(self):
        self.PopulationSizeText = self.NumberAliveFont.render('Population Size: ' + str(Population.Size), True, self.NumberAliveColor, None)
        Screen.Display.blit(self.PopulationSizeText, (234, 5))


    def MakePipe(self):
        if self.Pipe.x < -112:
            self.Pipe = pipe(randint(10, 20) * 10, 3, 5, {'Bottom': 'BottomPipe.png', 'Top': 'TopPipe.png'})
            self.CanScore = True


    def UpdateScore(self):
        if self.CanScore and self.Pipe.x < 140:
            self.Score += 1

            if self.Score > self.HighScore:
                self.HighScore = self.Score
                self.SaveHighScore()
                self.HighestGeneration = Population.Generation

            self.CanScore = False


    def Draw(self):
        self.Inputs()
        self.MakePipe()
        self.Pipe.Update()
        self.Pipe.Draw()




        self.Length = len(Population.Population)
        for index, Bird in enumerate(Population.Population[::-1]):

            self.NeuralNetworkInputs = [Bird.y, Bird.Falling, Bird.Velocity, self.Pipe.x, self.Pipe.TopHeight, self.Pipe.BottomHeight]
            if Bird.Brain.Guess(self.NeuralNetworkInputs)[0]:
                Bird.Jump()

            Bird.Update()
            Bird.Draw()

            if Bird.Collision():
                Population.PossibleParents.insert(0, Population.Population.pop(self.Length - index - 1))

            Bird.Fitness += 1




        self.UpdateScore()

        Screen.Move()
        Screen.Update()




def ReLU(Number):
    if Number >= 0:
        return Number
    return 0


def MatrixFromArray(List):
    Thing = matrix(len(List), 1)
    for index, item in enumerate(List):
        Thing.Data[index][0] = item

    return Thing


def ArrayFromMatrix(Matrix):
    List = []
    for Thing in Matrix.Data:
        for OtherThing in Thing:
            List.append(OtherThing)

    return List




def ReLU(Number):
    if Number >= 0:
        return Number
    return 0


def MatrixFromArray(List):
    Thing = matrix(len(List), 1)
    for index, item in enumerate(List):
        Thing.Data[index][0] = item

    return Thing


def ArrayFromMatrix(Matrix):
    List = []
    for Thing in Matrix.Data:
        for OtherThing in Thing:
            List.append(OtherThing)

    return List




class matrix():


    def __init__(self, Rows, Columns):
        self.Rows, self.Columns = Rows, Columns

        self.Data = []
        for i in range(self.Rows):
            self.Data.append([])
            for _ in range(self.Columns):
                self.Data[i].append(uniform(-1, 1))


    def MultiplyMatrix(self, Matrix, Return=False):

        self.Temporary = matrix(self.Rows, Matrix.Columns)


        for i in range(self.Rows):
            self.TemporaryNumber = 0
            for j in range(Matrix.Rows):
                self.TemporaryNumber += self.Data[i][j] * Matrix.Data[j][0]
            self.Temporary.Data[i][0] = self.TemporaryNumber


        if Return:
            return self.Temporary
        self.Data = self.Temporary.Data


    def AddMatrix(self, Matrix, Return=False):
        if Return:
            self.Temporary = matrix(self.Rows, self.Columns)
            for i in range(len(self.Data)):
                for j in range(len(self.Data[i])):
                    self.Temporary.Set(i, j, self.Data[i][j] + Matrix.Data[i][j])
            return self.Temporary

        for i in range(len(self.Data)):
            for j in range(len(self.Data[i])):
                self.Data[i][j] = self.Data[i][j] + Matrix.Data[i][j]


    def Map(self, Function, Return=False):
        if Return:
            self.Thing = self.Copy()
            for i in range(self.Rows):
                self.Thing.Data[i] = list(map(Function, self.Data[i]))

            return self.Thing

        for i in range(self.Rows):
            self.Data[i] = list(map(Function, self.Data[i]))




class neuralNetwork():


    def __init__(self, Inputs, Hiddens, Outputs):
        self.Inputs  = Inputs
        self.Hiddens = Hiddens
        self.Outputs = Outputs

        self.InputHidden_Weights  = matrix(self.Hiddens, self.Inputs)
        self.HiddenBiases         = matrix(self.Hiddens, 1)

        self.HiddenOutput_Weights = matrix(self.Outputs, self.Hiddens)
        self.OutputBiases         = matrix(self.Outputs, 1)


        self.Weights = [self.InputHidden_Weights, self.HiddenBiases, self.HiddenOutput_Weights, self.OutputBiases]


    def Mutate(self, Rate):
        for Thing in self.Weights:
            for OtherThing in Thing.Data:
                for i in range(len(OtherThing)):
                    self.Number = random()
                    if self.Number < Rate:
                        OtherThing[i] = uniform(-1, 1)


    def Guess(self, Inputs):
        self.Inputs = MatrixFromArray(Inputs)

        self.HiddenValues = self.InputHidden_Weights.MultiplyMatrix(self.Inputs, True)
        self.HiddenValues.AddMatrix(self.HiddenBiases)
        self.HiddenValues.Map(ReLU)

        self.Outputs = self.HiddenOutput_Weights.MultiplyMatrix(self.HiddenValues, True)
        self.Outputs.AddMatrix(self.OutputBiases)
        self.Outputs.Map(ReLU)

        return ArrayFromMatrix(self.Outputs)




class population():


    def __init__(self, Size, MutationRate):
        self.Size = Size
        self.Population = []
        self.PossibleParents = []
        self.Generation = 1

        for i in range(self.Size):
            self.Population.append(bird(Screen.Width//2, 10.5, 0.98, 1.03, 38, 25, 5, 12, 'Bird.png'))

        self.MutationRate = MutationRate


    def Run(self):
        Game.Draw()


    def FindStats(self):

        self.Total = 0

        for Thing in self.PossibleParents:
            self.Total += Thing.Fitness


        for Thing in self.PossibleParents:
            Thing.Probability = Thing.Fitness / self.Total


    def Choose(self):
        self.Index = -1
        self.Number = random()

        while self.Number > 0:
            self.Index += 1
            self.Number -= self.PossibleParents[self.Index].Probability

        self.NewBrain = deepcopy(self.PossibleParents[self.Index].Brain)
        self.NewBrain.Mutate(self.MutationRate)


        return self.NewBrain


    def Breed(self):
        if len(self.Population) == 0:
            self.FindStats()
            self.NewBrains = []

            for i in range(len(self.PossibleParents)):
                self.NewBrains.append(self.Choose())

            for i in range(self.Size):
                self.Population.append(bird(Screen.Width//2, 10.5, 0.98, 1.03, 38, 25, 5, 12, 'Bird.png'))
                self.Population[i].Brain = self.NewBrains[i]

            Game.Pipe = pipe(randint(10, 20) * 10, 3, 5, {'Bottom': 'BottomPipe.png', 'Top': 'TopPipe.png'})
            self.PossibleParents.clear()
            self.Generation += 1
            Game.Score = 0
            Game.CanScore = True




def Main():
    global Game, Screen, Population
    Game = game()
    Screen = screen(400, 400, 60, 2, {'Bottom': 'BackgroundBottom.png', 'Top': 'BackgroundTop.png'})
    RunBestBird = int(input('Run last saved bird? '))

    if RunBestBird:
        from re import findall

        Population = population(1, 0.01)
        Bird = bird(Screen.Width//2, 10.5, 0.98, 1.03, 38, 25, 5, 12, 'Bird.png')


        File = open("BestBird.data", 'r')
        Data = File.read()
        File.close()

        Values = findall(r"-?\d+\.\d+", Data)


        Data = [float(Item) for Item in Values]


        Index = 0

        for i in range(10):
            for j in range(6):
                Bird.Brain.InputHidden_Weights.Data[i][j] = Data[Index]
                Index += 1

        for i in range(10):
            Bird.Brain.HiddenBiases.Data[i][0] = Data[Index]
            Index += 1

        for i in range(10):
            Bird.Brain.HiddenOutput_Weights.Data[0][i] = Data[Index]
            Index += 1

        Bird.Brain.OutputBiases.Data[0][0] = Data[Index]
        Population.Population[0] = Bird

        while True:

            Population.Run()

            if len(Population.Population) == 0:
                pygame.quit()
                exit()




    else:
        Population = population(int(input("Population size: ")), 0.01)
        while True:
            Population.Run()
            Population.Breed()




if __name__ == "__main__":
    Main()
