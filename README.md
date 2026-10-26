# FitForge : Your Personal Trainer

## Overview :
FitForge is a personal trainer that works on the command line (CLI). It asks the trainee about his body (height, weight, age) and his goal, then calculates his daily calories and builds him a complete weekly workout plan (Full Body, Upper / Lower or Push / Pull / Legs) based on how many days and hours he can train. It also calculates the calories he will burn in every workout, guides him through his workout set by set, tracks his progress until he reaches his target weight, and optionally provides an AI coach.

## Features & User Stories
As a trainee I should be able to do the following :

* Create my profile by answering the coach's questions (height, weight, age, goal, days & hours of training).
* See my BMI and the healthy weight range for my height.
* Know how many calories I should eat on a rest day and on a training day.
* Get my daily protein, carbs, fat and water.
* Get a weekly workout plan that fits my days and hours (Full Body, Upper / Lower or Push / Pull / Legs).
* Choose if I train at the gym or at home.
* See the exercises of any day with sets, reps and rest time.
* See how many calories I will burn in every exercise, every workout and every week.
* Start a guided workout where the coach shows me each exercise and counts my sets.
* Replace an exercise I don't like with another one.
* Search for exercises and view their info and coaching tips.
* Log my weight and see my progress.
* Know how many weeks I need to reach my target weight.
* Unlock achievements when I make progress.
* Edit my profile and get a new plan.
* Save my plan to a file.
* Chat with an AI coach that considers my profile, today's nutrition, weekly plan and recent workouts.
* Ask the AI coach a quick question or request three tips based on my plan and progress.

## Usage :
To start the program type in `python main.py`, answer the coach's questions, then :

* type in `help` to show all the commands.
* type in `stats` to show your BMI, calories, macros and water.
* type in `profile` to show your profile.
* type in `edit` to answer the questions again and get a new plan.
* type in `back` during profile questions to return to the previous question; earlier answers stay as defaults.
* type in `weight number` to log your weight (example : `weight 82.5`).
* type in `plan` to show your weekly workout plan.
* type in `today` to show today's workout.
* type in `day day_name` to show the exercises of a day (example : `day monday`).
* type in `start` to start today's workout with the coach.
* type in `swap exercise_name with exercise_name` to replace an exercise (example : `swap Deadlift with Pull-Up`).
* type in `regen` to make a new plan.
* type in `export` to save your plan to a file.
* type in `search exercise_name` to search for an exercise.
* type in `exercise exercise_name` to get information about this exercise.
* type in `library` to show all the exercises.
* type in `progress` to show your workouts and weight progress.
* type in `forecast` to know when you will reach your target weight.
* type in `badges` to show your achievements.
* type in `switch` to change the user.
* type in `exit` to save and quit.
* type in `coach` to chat with the AI coach (type `back` to return).
* type in `ask what should I eat after training?` to ask one quick question.
* type in `review` to get three tips for this week based on your plan and progress.

## Setup AI Coach
The AI coach is optional; the rest of FitForge works without an API key. Copy `.env.example` to `.env`, then replace `your-key-here` with your Anthropic API key. The app reads `ANTHROPIC_API_KEY` from `.env` or the environment. Keep `.env` private and do not commit it. To choose a different Anthropic model, set `FITFORGE_MODEL`; the default is `claude-sonnet-5-5`.