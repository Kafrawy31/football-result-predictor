# Intro

Can we predict the unpredictable? Football is a game of passion, strategy, and a fair bit of chaos, but what if we could unravel its patterns using data? This project dives into the art and science of predicting full-time results for football games. Combining statistical models, advanced machine learning techniques, and custom-engineered metrics, this journey explores the interplay between numbers and the beautiful game. Whether you’re a data enthusiast or a football fanatic, this project offers insights into the cutting-edge approaches to understanding football outcomes.

# Video overview

# Table of contents

- Data collection
- Data engineering
  - MLE parameters
- Elo & Glicko2
- Clustering
  - K-Means
  - Archetypal
- Models
  - Statistical
    - Poisson modelling
    - Dixon-Cole modelling
  - Machine Learning / Deep Learning
    - Random Forest Classifier
    - Random Forest Regressor
    - Artificial Neural Networks
      - Stacking with Dixon-Cole model matrices
    - Multi Headed LSTMs
- Making predictions & staying up to date
- Results
- Future work and improvements

# Data collection

I used data from two different sources.

1.) football-data.co.uk
2.) sofascore.com

football-data.co.uk had data for majority of the European leagues and also included the betting odds for different bookies. However, this website included simpler statistics and only contained team level metrics. (Goals, Assists, shots on target, etc..). This website contained csvs that update each week after games are played.

sofascore.com on the other hand had more complex team level statistics such as (possession, final third entries, ground duels won, aerial duels won, etc..). SofaScore also included player level metrics including minutes played and player ratings. This was especially useful when calculating player elo's. I had to scrape the data from this website.

# Data engineering

Using sofascore statistics I calculated some advanced football metrics that help capture team strengths and weaknesses that the lower level metrics do not capture.

Some of the most notable ones are
1.) XGc: Expected goal contributions
2.) XDs: Expected disruption score
3.) Duel Power
4.) Pressure Index

### xGC

XGc combines shooting efficiency, big chance conversion rate and total shots on target per game. Where shooting efficiency is shots on goal/total shot attempts and conversion rate is big chance created / big chance scored.

### Duel Power

Duel power is how often teams win aerial 50/50s and ground 50/50s

### Pressure Index

A teams pressure index is how much defensive pressure a team will apply per opposition team shot. The calculation for this was (blocked scoring attempt + interceptions won + clearances) / opposition team shots on target.
If the opposition team got 0 shots on goal, then the pressure index gets a small multiplier of 1.2.

I also calculated other metrics such as pass disruption rate, territorial dominance and final third efficiency.

## MLE parameters

I used an MLE algorithm to determine the best attacking and defensive parameters for each team within a given league. This algorithm used the number of goals scored and conceded by each team to determine the attack and defensive parameters per team. I also vectorized the data to speed things up since the MLE algorithm takes quite a lot of time.

# Elo & Glicko2

I created Elo and Glicko2 engines to determine team strengths, and used a different Elo engine to calculate player strengths

## Team Level calculations

### Elo

I modified the base Elo function to account for 2 things.

1.) Margin of victory
2.) The underlying 50% draw probability assumption

The base Elo calculation assumes that each game played has a probability of 50% for a draw which is not the case in our context, however there is another function called the Davidson-Elo function which introduces a mu parameter which can be tweaked by the user to change that percentage.

I also included a margin of victory parameter that increases the elo points gained / lost logarithmically.

### Glicko2

I included the same margin of victory parameter in the glicko2 algorithm, this was a bit more complicated since Glicko2 creates 3 scores for each team. The strength rating, the reliability of that rating and the volatility of a teams performance. This algorithm also includes a tau parameter which when greater increases the volatility of the system meaning that team ratings deviate quicker, the higher this value was the better the results, however after a certain value the algorithm breaks since the numerical stability decreases as tau increases

## Player level calculations

I used the Elo engine to calculate the player strengths. This was more complicated so here's a breakdown. I had to find out the average rating for players in each position (forward, midfielder, defender, goalkeeper) to make this engine work.

- Team lost
  1.) Player had an above average rating: The elo penalty is reduced depending on how well the player performed multiplied by the minutes played / 90
  2.) Player had a below average rating: The elo penalty is amplified depending on how bad the player performed multiplied by the minutes played / 90

- Team drew

  - Team expected to win
    1.) Player had an above average rating: The elo penalty is reduced depending on how well the player performed multiplied by the minutes played / 90
    2.) Player had a below average rating: The elo penalty is amplified depending on how bad the player performed multiplied by the minutes played / 90

  - Team expected to lose
    1.) Player had an above average rating: The elo reward is amplified depending on how well the player performed multiplied by the minutes played / 90
    2.) Player had a below average rating: The elo reward is reduced depending on how bad the player performed multiplied by the minutes played / 90

- Team won
  1.) Player had an above average rating: The elo reward is amplified depending on how well the player performed multiplied by the minutes played / 90
  2.) Player had a below average rating: The elo reward is reduced depending on how bad the player performed multiplied by the minutes played / 90

# Clustering

## K-means

This clustering method didn't really work, I clustered teams based on their metrics and wins / losses, the optimum number of clusters was 6, I used the confidences of a team to belong in each cluster as inputs

## Archetypal clustering

This is a lesser known clustering method but instead of grouping teams around average points like k-means clustering does, this algorithm represent each data point as a convex combination of archetypes, which are extreme points located at the edges of the data distribution.
Which means that archetypes are often at the 'corners' of each data type. What this does is highlights extreme patterns/'prototypes'.
This finds archetypes by minimizing the reconstruction error, representing each data point as a weighted sum of the archetypes.
This ended up working better than k-means clustering

# Models

## Statistical models

### Poisson Modelling

Poisson Modelling is a statistical approach used to model count-based data, where the goal is to predict the likelihood of events occurring within a fixed interval (e.g., time, space, or matches). In the context of football, Poisson modelling is commonly used to predict the number of goals scored by each team in a game.

The inputs for this model were the MLE algorithms attack and defense parameters for each team. So teams with higher attack parameters are expected to score more, and teams with higher defense parameters are expected to concede less.

The output from this model was a distribution of percentages for the expected number of goals for each team to score. Eg. (0:11%, 1:15%, 2:33%, etc.). The distributions are then multiplied together to create a matrix, and using that matrix; home, draw and away win probabilities are calculated.

Pros:

- Can calculate most probable outcomes
- Good for calculating most probable goal ranges
- Can be used for corners, fouls, yellow cards, shots on target etc.

Cons:

- Poor at identifying low scoring games
- Weighs all games the same, no extra weighing for more recent games.
- Poor full time result accuracy: 49%

### Dixon-Cole Modelling

Dixon-Cole modelling is fundamentally similar to Poisson modelling but introduces both a correction factor and a time decay factor. Like Poisson, the inputs and outputs are the same.

#### Correction Factor

The correction factor is added to the model to account for the inflated probability of draws. This improves the accuracy of predicting low-scoring games or games where the score difference is minimal

#### Decay parameter

A time decay parameter ensures that more recent matches carry more weight in the calculations, which reflects current team strengths and form more accurately.

Pros:

- Better at predicting low-scoring games and draws
- More realistic adjustments
- Beats the over/under goals market with 20% ROI when back-tested
- Good at predicting the number of goals in a game

Cons:

- Requires careful tuning of correction and decay parameters.
- Only uses attack and defense parameters, very limited inputs
- Poor full time result prediction accuracy: 52%

# Machine and Deep learning models

## Random forest Classifier & Regressor

When using the Random Forest Classifier I got to use all the engineered parameters, along with the attack and defense parameters. I also used an aggregated Elo of the starting 11 before games started.

The classifier model achieved a 54% on home/draw/away predictions while the regressor achieved a 51% accuracy.

## Neural Networks

This model was tougher to get to work. I tried different approaches and different inputs with the neural networks. I tried a total of x approaches.
I used these models for home/away predictions. These were not used to predict draws

1.) Elo/Glicko + attack/defense parameters
2.) Elo/Glicko + attack/defense parameters + matrix output from Dixon-cole model
3.) Elo/Glicko + attack/defense parameters + matrix output from Dixon-cole model + league embeddings
4.) Elo/Glicko + attack/defense parameters + matrix output from Dixon-cole model + league embeddings + team embeddings

### Approach 1: Power ratings

This approach only used power ratings using a simple feed forward neural network. After parameter tuning, this achieved a a 65% accuracy.

### Approach 2: Power ratings + Dixon-Cole model matrices

I tried two different approaches with using this strategy. The first one involved flattening the matrices and using a single dense layer and the second one involved using a convolutional layer to go over the matrices & a second neural dense layer. However, I opted for the second approach since it produces more consistent results

They both achieved similar accuracies varying between 67-68%

### Approach 3: Power Ratings + league embeddings + Dixon cole matrices

Similar to the previous approach I used a dense layer for the power ratings, a convolutional layer and finally an attention layer to process the league embeddings. This massively increased the accuracy up to 70-72%. This indicates the differences between each league. The best performing leagues on average were:

- Liga Portugal: 41 predictions ~ 80% accuracy
- Ligue 1: 55 predictions ~ 76% accuracy
- Europa League: 23 predictions ~ 73% accuracy
- La Liga: 66 predictions ~ 72% accuracy
- Premier League: 62 predictions ~ 71% accuracy

Some of the worse performers being:

- Champions League: 32 predictions ~ 62% accuracy
- Championship: 92 predictions ~ 65% accuracy
- Brazilian League: 70 predictions ~ 67% accuracy

### Approach 4: Power Ratings + Dixon cole matrices + league embeddings + team embeddings

This model used the same architecture as the previous model, with an extra layer for team embeddings. This ended up performing worse than the previous model. Achieving around 67%-69% accuracy. It also seemed to be pretty inconsistent. This could indicate that the team embeddings were not capturing relationships well.

## LSTMs

I had to change the way I handled my data to make the lstms work. Instead of each row containing home and away teams, I split each row into two rows such that each row will have that game played from each teams perspective and included an extra column that indicates if the team is home or away. This was so I can create sequences that can be easier to manage and interpret by the lstm heads

I tested two different LSTM models:
1.) Two LSTM heads one for the home team and one for the away team
2.) LSTM head for each team.

For the LSTM approaches I only used data from the premier league and only used team level metrics (power ratings, advanced metrics, attack/defense parameters) (no player elos were used)

### Two LSTM heads

This was a straight forward approach, sequences of length 38 games, which is the number of games played by a team in a single season in the premier league. The architecture was made up of two LSTM heads that each process each teams last 38 games, followed by a dense layer. This model achieved around 73% accuracy which is only a small jump from the accuracy achieved by using the neural network approach.

### Multi-Headed LSTM approach

This approach involved creating LSTM heads for each team. The model would load in the heads for each team that it is about to train on. Let's call the heads current head and opponent head.
When the heads are loaded in, the opponent head is frozen and the current head is trained. After each epoch, all the heads are tested against the test set and their best scores are saved. Only the best performing heads are loaded in, that means that if one teams head overfits before other heads, that head will not have a compounding effect on training the other heads.

This was the best performing model out of all the models tested. Scoring 60% on home/away/draw predictions and 79% on home/away predictions

# Making predictions and staying up to-date

## Making predictions

To make predictions I had a function that would scrape all the games from the leagues that I have trained my model on for a given date. I enter the date into the function, all the games are grabbed, along with the lineups. They are fed into the appropriate models and a csv is generated that contains the confidence percentage along with the predicted result.

## Staying up to date

Since teams forms make a big difference, the data has to be updated day by day, so once the games are played for that day, another function appends the games into my data files.

# Result table

| **Model**                       | **Prediction Type** | **Accuracy (%)** |
| ------------------------------- | ------------------- | ---------------- |
| **Poisson Modelling**           | Home/Draw/Away      | 49%              |
| **Dixon-Cole Modelling**        | Home/Draw/Away      | 52%              |
| **Random Forest Classifier**    | Home/Draw/Away      | 54%              |
| **Random Forest Regressor**     | Home/Draw/Away      | 51%              |
| **Neural Network (Approach 1)** | Home/Away           | 65%              |
| **Neural Network (Approach 2)** | Home/Away           | 67-68%           |
| **Neural Network (Approach 3)** | Home/Away           | 70-72%           |
| **Neural Network (Approach 4)** | Home/Away           | 67-69%           |
| **Two LSTM Heads**              | Home/Away           | 73%              |
| **Multi-Headed LSTM**           | Home/Away/Draw      | 60%              |
| **Multi-Headed LSTM**           | Home/Away           | 79%              |
