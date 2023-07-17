# Github Issues

We will follow a form of issue driven development, and therefore we want to ensure that we have the correct labels and formats for all our issues.

## Github Issue Labels

https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad4/labels

Here we have listed all the issue labels to be used in the project. Some examples are "bug" or "enhancement".
All issues that are created must be given a label from above.

## Milestones

Milestones act as categorization for issues. We have milestones regarding each Sprint and then we can apply it to any issues we make.

## Github Project

All team members will have access to the github project, where we can create issues and move them between:

* To Do
* In Progress
* Done

Ensure all issues are created with labels and assign the correct individuals to each issue.
Also apply the correct milestone to every issue, regarding what point in the development we are at.

There will be issue templates available:

* Feature request template
* Bug report template

This means we can have a fixed layout for the most important issues.

# Branching Strategy

When working on code, we want to ensure that we effectively create a distinction between public branches and development branches. By having an effective formula and following a form issue driven development, proper organisation can be implemented.

We can split the majority of issue labels into two types of issues.

### Feature

This is not only new features.
It can also be low priority bugs.

### Hotfix

High priority bugs, critical.

## Types of Branches

### Main Branch

`main`: This branch is the latest production-ready version of the application. Any code in this branch must be stable and tested.

### Development branch

`dev`: This branch is the latest development-ready version of the application. All new features and hotfixes should be merged into this branch for testing and integration. The code will be reviewed by the lead developers when a merge request is created from the feature/hotfix branches. 

Additionally, a linter will be implemented in a workflow to ensure code-style is consistent.

When a lead developer determines that code is not up to standard a code review issue will be created for the branch to be updated with better code.

### Feature branch

`feature/issue[id]`: These branches are used to develop new features as well as fix bugs. They should be branched off the `dev` branch and merged back into it. The id in the branch name must be the issue number of the feature/bugfix being implemented.

### Hotfix branch

`hotfix/issue[id]`: These branches are used solely to fix very `critical` bugs. They should be branched off the `main` branch and merged back into it. The id in the branch name must be the issue number of the hotfix.

# Additional Guidelines

* Keep branches focused to the single feature we want to fix
* Pull latest changes from `dev` before creating a new feature branch
* Delete feature branches after they have been merged.
* Issue and Milestones must be used to track work.
* Merging code directly into `main` to `dev` without first testing and reviewing it thoroughly.

