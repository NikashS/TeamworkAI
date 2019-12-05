import random
#from game import ball_state

class SoccerAgent:
    def __init__(self, playerNum):
        self.Qvalues = dict([])
        self.epsilon = 0.01
        self.alpha   = 0.4
        self.episodeRewards = 0.0
        self.discount = 1.0
        # 1 or 2
        self.id = playerNum
    
    def getLegalActions(self, state):
        if state:
            return ["pass", "shoot", "hold"]
        return ["wait"]

    def getQValue(self, state, action):
        # not yet defined...
        if state not in self.Qvalues.keys():
          self.Qvalues[state] = dict([])
          actions = ["pass", "shoot", "hold", "wait"]
          # non-terminal check
          if actions:
            # initialize all Q(s, a) for a given s
            for a in actions:
              self.Qvalues[state][a] = 0.0
          return 0.0
        # exists, return Q(s, a)
        return self.Qvalues[state][action]
    
    def computeValueFromQValues(self, state):
        actions = self.getLegalActions(state)
        # terminal state
        if not actions:
          return 0.0
        # find max Q(s, a)
        return max([self.getQValue(state, a) for a in actions])

    def computeActionFromQValues(self, state):
        actions = self.getLegalActions(state)
        # terminal state
        if not actions:
          return None
        # find best action
        action = (actions[0], self.getQValue(state, actions[0]))
        for a in actions:
          q = self.getQValue(state, a) 
          # update
          if q > action[1]:
            action = (a, q)
          # random tie-breaker
          elif q == action[1]:
            action = random.choice(( (a, q), action ))
        return action[0]

    def getAction(self, state):
        # Pick Action
        legalActions = self.getLegalActions(state)
        action = None
        # terminal state
        if not legalActions:
          return None
        # random action or not?
        if random.random() < self.epsilon:
          # random
          action = random.choice(legalActions)
        else:
          # choose best policy
          action = self.computeActionFromQValues(state)
        return action
    
    def update(self, state, action, nextState, reward):
        # find q = argmax(Q(s', a))
        q = self.computeValueFromQValues(nextState)
        Q = (1 - self.alpha)*self.getQValue(state,action) + self.alpha*(reward + self.discount*q)
        # assign to Q(s, a)
        self.Qvalues[state][action] = Q

    def observeTransition(self, state, action, nextState, delta):
        self.episodeRewards += delta
        self.update(state, action, nextState, delta)