"""
The template of the script for the machine learning process in game pingpong
python MLGame.py -i ml_play_LR_210112.py -i ml_play_LR_210112.py pingpong EASY
"""


import random
import pickle
import numpy as np
class MLPlay:
    def __init__(self, side):
        """
        Constructor
        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.ball_served = False
        self.side = side
        self.difficulty = "EASY"
        #------------------------------------------若是讀入相對的.SAV檔---------------------------------

        if self.side == "1P":
            filename = "C:\\LR_example_1P_right.sav"
            self.model_right = pickle.load(open(filename,'rb'))
            filename = "C:\\LR_example_1P_left.sav"
            self.model_left = pickle.load(open(filename,'rb'))
        elif self.side == "2P":
            filename = "C:\\LR_example_2P_right.sav"
            self.model_right = pickle.load(open(filename,'rb'))
            filename = "C:\\LR_example_2P_left.sav"
            self.model_left = pickle.load(open(filename,'rb'))
        
    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            print(scene_info["ball_speed"])
            return "RESET"
        
        if abs(scene_info["ball_speed"][0]) != abs(scene_info["ball_speed"][1]):#偵測到切球，則切換成NORNAL模式
            self.difficulty = "NORMAL"
        if self.difficulty == "NORMAL" :#若難易度為NORMAL以上，則讓板子隨機切球
            hit_deep = 18
        else:
            hit_deep = 15
            

        
        
        #-------------------------------------------有發球權的一方進行發球程序---------------------------------------------------
        if self.ball_served == False:
            if self.side == "1P" and scene_info['ball'][1]>420-5-1:
                return (self.serve_ball(scene_info["platform_1P"][0]))
            elif self.side == "2P" and scene_info['ball'][1]<80+1:
                return(self.serve_ball(scene_info["platform_2P"][0]))
            
        if scene_info["frame"] == 0:#遊戲開始時給定預設值
            self.ball_destination=100
            
        if scene_info["status"] != "GAME_ALIVE":#若偵測到遊戲結束，則重新開局
            return "RESET"

        if self.side == "1P":
            platform_edge_x = scene_info["platform_1P"][0]+35#Get platform1 location
            if scene_info['ball'][1]>420-5-1 : #如果球在 1P 擊出，則預測下一次回來的位置 
                inp_temp = np.array([scene_info["ball"][0],scene_info["ball_speed"][0], scene_info["ball_speed"][1]])
                input = inp_temp[np.newaxis, :]
                if scene_info["ball_speed"][0] > 0 :#求若往右側打，則預測往右側的球路
                    self.ball_destination = self.model_right.predict(input)
                if scene_info["ball_speed"][0] < 0 : #求若往左側打，則預測往左側的球路
                    self.ball_destination = self.model_left.predict(input)
                
            if scene_info["ball_speed"][1]>0:#球若是往1P處移動則計算球的落點，並將板子往落點移動
                self.ball_destination = scene_info["ball"][0]+ (((420-5-scene_info["ball"][1])/scene_info["ball_speed"][1])*scene_info["ball_speed"][0])
                while self.ball_destination < 0 or self.ball_destination > 195:
                    if self.ball_destination < 0:
                        self.ball_destination = -self.ball_destination
                    if self.ball_destination > 195:
                        self.ball_destination = 195-(self.ball_destination-195)
                if self.ball_destination < scene_info["platform_1P"][0]+hit_deep:
                    command = "MOVE_LEFT"
                elif self.ball_destination > platform_edge_x-hit_deep:
                    command = "MOVE_RIGHT"
                else:
                    command = "NONE"
                    
                return command
            elif scene_info["ball_speed"][1]<0:#球若是往2P處移動，則將板子往預測的落點移動
                if self.ball_destination < scene_info["platform_1P"][0]+hit_deep:
                    command = "MOVE_LEFT"
                elif self.ball_destination > platform_edge_x-hit_deep:
                    command = "MOVE_RIGHT"
                else:
                    command = "NONE"
                return command
        elif self.side == "2P":
            platform_edge_x = scene_info["platform_2P"][0]+35#Get platform2 location
            if scene_info['ball'][1]<80+1 : #如果球在 2P 擊出，則預測下一次求回來的位置 
                inp_temp = np.array([scene_info["ball"][0],scene_info["ball_speed"][0], scene_info["ball_speed"][1]])
                input = inp_temp[np.newaxis, :]
                if scene_info["ball_speed"][0] > 0 :#求若往右側打，則預測往右側的球路
                    self.ball_destination = self.model_right.predict(input)
                if scene_info["ball_speed"][0] < 0 : #求若往左側打，則預測往左側的球路
                    self.ball_destination = self.model_left.predict(input)
            if scene_info["ball_speed"][1]<0:#球若是往2P處移動則計算球的落點，並將板子往落點移動
                self.ball_destination = scene_info["ball"][0]+ (((80-scene_info["ball"][1])/scene_info["ball_speed"][1])*scene_info["ball_speed"][0])
                while self.ball_destination < 0 or self.ball_destination > 195:
                    if self.ball_destination < 0:
                        self.ball_destination = -self.ball_destination
                    if self.ball_destination > 195:
                        self.ball_destination = 195-(self.ball_destination-195)
                if self.ball_destination < scene_info["platform_2P"][0]+hit_deep:
                    command = "MOVE_LEFT"
                elif self.ball_destination > platform_edge_x-hit_deep:
                    command = "MOVE_RIGHT"
                else:
                    command = "NONE"
                return command
            elif scene_info["ball_speed"][1]>0:#球若是往1P處移動，則將板子往預測的落點移動
                if self.ball_destination < scene_info["platform_2P"][0]+hit_deep:
                    command = "MOVE_LEFT"
                elif self.ball_destination > platform_edge_x-hit_deep:
                    command = "MOVE_RIGHT"
                else:
                    command = "NONE"
                return command
        
            #inp_temp = np.array([ball_arrive_locat[0][0],right_speed])
   
    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
    
    def serve_ball(self, platform):

        if self.difficulty == "EASY":
            ball_destination = 45
            serve_to = "SERVE_TO_LEFT"
        elif self.difficulty == "NORMAL":
            ball_destination = 125
            serve_to = "SERVE_TO_RIGHT"
        else:
            ball_destination=100
            serve_to = random.choice(["SERVE_TO_LEFT","SERVE_TO_RIGHT"])
            
        if ball_destination < platform + 20 :
            return "MOVE_LEFT"
        elif ball_destination > platform + 20 :
            return "MOVE_RIGHT"
        else:
            self.ball_served = True
            return serve_to



