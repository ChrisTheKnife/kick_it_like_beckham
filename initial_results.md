### "Money"-Features

* 'pledged' is in local currency and should not be used in the model --> 'converted_pledged_amount' or 'usd_pledged' should be used here, since they have nearly the same numbers
* 'goal' is also the amount of money in local currency --> 'goal_usd' will be engineered
* For checking if the goal was surpassed, two features were engineered:
    - 'goal_surpass' --> surpass in local currency --> do NOT use in model
    - 'goal_surpass_usd' --> converted in USD --> USE in the model
    - 'goal_surpass_share' --> share of the surpass based on goal, "relative surpass" --> can be used in the model

### Facts and outliers in the money features

* Project id 1947298033 had 1$ as goal and collected 68763$, so the 'goal_surpass-share' is also 68763, while the mean share is only 3.7 and 75% of shares are below 0.23 --> could be regarded as an outlier.
* 200000$ is the highest goal within the successful projects.
* Failed projects go up to 150 mio $ --> 'goal_usd' should be scaled?
* The higher the goal the more projects will fail.
* 3 observations surpassed the goal but nevertheless failed (1085047405, 1880688778, 1090065437) --> Shall be removed??
* 246 successful + 17 failed projects stated a goal of 1$
* What to do with projects with high goals and 0 backers?