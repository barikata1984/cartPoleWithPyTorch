import gym
import numpy as np
from random import random

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

###########################################
# Basic Concept of Reinforcement Learning
###########################################
#
# !! ATTENITON !! 
# !! THE FOLLOWING COMMENTED OUT CODES DO NOT WORK !!
# !! JUST A DESCRIPTOIN OF FUNDAMENTAL CONCEPT !!
#
# while True:
#     action = select_action(state)
#     staet, _, done, _ = env.step()
#     env.render()
#     if done:
#         break
#
###########################################

# With '-v1', the environemnt comes with 500 timesteps.
# In contrast, the environment with '-v2' comes with 200 timesteps.
env = gym.make('CartPole-v1')
print(env._max_episode_steps)

def select_action_random(state):
    if random() < 0.5:
        return 0
    else:
        return 1

def select_action_simple(state):
    if state[2] < 0:    # Cart Velocity 
        return 0
    else:
        return 1

def select_action_good(state):
    if state[2] + state[3] < 0: # Cart Velocity and Pole Angle 
        return 0
    else:
        return 1

def goodness_score(select_action, num_episodes = 100):
    num_steps = 500
    ts = []
    for episode in range(num_episodes):
        state = env.reset()
        for t in range(1, num_steps + 1):
            action = select_action(state)
            state, _, done, _ = env.step(action)
            if done:
                break
        ts.append(t)
    score = sum(ts) / (len(ts) * num_steps)
    return score

print("Score for the RANDOM policy: %f" % goodness_score(select_action_random))
print("Score for the SIMPLE policy: %f" % goodness_score(select_action_simple))
print("Score for the GOOD policy: %f" % goodness_score(select_action_good))

class PolicyNN(nn.Module):
    def __init__(self):
        super(PolicyNN, self).__init__()
        self.fc = nn.Linear(4, 2)   # use the linear transformer with 4 input and 2 output" 

    def forward(self, x):
        x = self.fc(x)
        return F.softmax(x, dim = 1)

def select_action_from_policy(model, state):
    state = torch.from_numpy(state).float().unsqueeze(0)
    probs = model(state)
    m = Categorical(probs)
    action = m.sample()
    return action.item(), m.log_prob(action)

def select_action_from_policy_best(model, state):
    state = torch.from_numpy(state).float().unsqueeze(0)
    probs = model(state)
    if probs[0][0] > probs[0][1]:
        return 0
    else:
        return 1

model_untrained = PolicyNN()

print(
    goodness_score(lambda state: select_action_from_policy(model_untrained, state)[0]),
    goodness_score(lambda state: select_action_from_policy_best(model_untrained, state))
) 

def train_wont_work(num_episodes = 1000):
    num_steps = 500
    for episode in range(num_episodes):
        state = env.reset()
        for t in range(1, num_steps + 1):
            action = select_action_from_policy(state)
            state, _, done, _ = env. step(action)
            if done:
                break
            loss = 1.0 - t / num_steps
            # this does not actually work, because the loss 
            # function is not an explicit function of the model's 
            # output; it is a functin of book keping variables.
            optimizer.zero_grad()
            loss.backward() # AttributeError: 'float' object no attribute 'backward'
            optimizer.step()

model = PolicyNN()
optimizer = optim.Adam(model.parameters(), lr = 0.01)

def train_simple(num_episodes = 10 * 1000):
    num_steps = 500
    ts = []
    for episode in range(num_episodes):
        state = env.reset()
        probs = []
        for t in range (1, num_steps + 1):
            action, prob = select_action_from_policy(model, state)
            probs.append(prob)
            state, _, done, _ = env.step(action)
            if done:
                break
        loss = 0

        for i, prob in enumerate(probs):
            loss += -1 * (t - i) * prob
        
        print(episode, t, loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        ts.append(t)
        
        # check stopping condition:
        if len(ts) > 10 and sum(ts[-10:]) / 10.0 >= num_steps * 0.95:
            print("Stopping training, looks good...")
            return

train_simple()

print(goodness_score(lambda state: select_action_from_policy_best(model, state)))