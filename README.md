# Mario Runner AI

<p align="center">
<img src="./examples/1.gif" alt="image not found" width="600">
</p>

## About The Project

Infinite platformer runner AI built using NeuroEvolution of Augmenting Topologies (NEAT).

### Built With

* [Python](https://www.python.org/)
* [NEAT](https://github.com/CodeReclaimers/neat-python)
* [Pygame](https://www.pygame.org)




## Getting Started

There are a few librarier that need to be installed in order for the app to work.

### Prerequisites
  ```sh
  npm install npm@latest -g
  ```

### Installation

1. Clone the repo

   ```sh
   git clone https://github.com/andreiec/mario-runner-ai.git
   ```
2. Install NPM packages

   ```sh
   npm install
   ```

## Usage

Mario Runner is built upon NEAT. A very simple to understand workflow of the algorithm is the following
1. Generate the initial population of players with random genomes
2. Since they are built randomly, some players might get further than others
3. Get the highest scoring players and breed their genomes to get the next generation
4. Generate the same amount of players, but with the new and improved genomes
5. Let them run until there are no more players
6. Loop through steps 3-5 <br /><br />

<p align="center">
<img src="./examples/2.gif" alt="iamge not found" width="500">
</p>

## Player Input
There are 3 values used for player input and one for the output (jump button)
* Distance to the next pipe
* Next pipe type
* Y-position of player

## User Input

`H` - Display HUD for generation information <br />
`K` - Kill all current players and move to next generation


## License

Distributed under the MIT License. See `LICENSE` for more information.
