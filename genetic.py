import numpy as np


class City:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_coordination(self):
        return str(str(self.x) + ' ' + str(self.y) + ' ' + str(self.z))

    def __eq__(self, other):
        if self is None or other is None:
            return False
        else:
            return self.x == other.x and self.y == other.y and self.z == other.z


class Path:
    def __init__(self, city_list:[City]):
        self.city_list = city_list
        self.total_distance = None
        self.probability = None

    def __eq__(self, other):
        return self.city_list == other.city_list

    def get_path_distance(self):
        if self.total_distance is None:
            self.compute_path_distance()
        return self.total_distance

    def compute_path_distance(self):
        total_distance = 0
        for i in range(len(self.city_list) - 1):
            current_city = self.get_city_by_index(i)
            next_city = self.get_city_by_index(i + 1)
            total_distance += compute_distance(current_city, next_city)

        # Get back to first city to complete the loop
        total_distance += compute_distance(self.city_list[0], self.city_list[-1])
        self.total_distance = total_distance

    def get_city_by_index(self, index):
        return self.city_list[index]

    def set_probability(self, all_distances_sum):
        self.probability = self.total_distance / all_distances_sum

    def get_probability(self):
        return self.probability


def compute_distance(first_city: City, second_city: City):
    return (((first_city.x - second_city.x) ** 2) + ((first_city.y - second_city.y) ** 2) + ((first_city.z - second_city.z) ** 2)) ** 0.5


def create_initial_population(population_size, city_list: [City]):
    initial_population: [Path] = []
    for i in range(population_size):
        path = Path(np.random.choice(city_list, len(city_list), replace=False).tolist())
        initial_population.append(path)
    return initial_population


def compute_all_distances(population:[Path]):
    for path in population:
        path.compute_path_distance()


def calculate_probabilities(population: [Path]):
    all_distances_sum = 0
    for path in population:
        all_distances_sum += path.get_path_distance()
    for path in population:
        path.set_probability(all_distances_sum)


def create_mating_pool(population):
    mating_pool_size = len(population) // 4

    # Since TSP is a minimization problem, the probabilities should be reversed
    rev_prob = [(1-path.get_probability()) for path in population]
    rev_prob = [p/sum(rev_prob) for p in rev_prob]

    mating_pool_1 = np.random.choice(population, mating_pool_size, p=rev_prob).tolist()
    mating_pool_2 = np.random.choice(population, mating_pool_size, p=rev_prob).tolist()

    return mating_pool_1, mating_pool_2


def crossover(parent_1: Path, parent_2: Path, num_cities):
    end_index = np.random.randint(1, num_cities)
    start_index = np.random.randint(0, end_index)
    child: Path = Path(parent_1.city_list[start_index:end_index])
    for city in parent_2.city_list:
        if city not in child.city_list:
            child.city_list.append(city)
    return child


def crossover_population(mating_pool_1: [Path], mating_pool_2: [Path], num_cities):
    children: [Path] = []
    for i in range(len(mating_pool_1)):
        children.append(crossover(mating_pool_1[i], mating_pool_2[i], num_cities))
    return children


def genetic_algorithm(population: [Path], num_cities):
    compute_all_distances(population)
    calculate_probabilities(population)
    mating_pool_1, mating_pool_2 = create_mating_pool(population)
    children: [Path] = crossover_population(mating_pool_1, mating_pool_2, num_cities)
    new_population = sorted(population, key=lambda path: path.get_probability())[0:(len(population) - len(children))]
    new_population.extend(children)
    return new_population


MAX_ITERATION = 800
POPULATION_SIZE = 20

num_cities = 0
city_list: [City] = []

with open('input.txt', 'r') as input_file:
    first = True
    for line in input_file.readlines():
        if first:
            num_cities = int(line)
            first = False
        else:
            splitted = line.split(' ')
            city_list.append(City(int(splitted[0]), int(splitted[1]), int(splitted[2])))

population: [Path] = create_initial_population(POPULATION_SIZE, city_list)

# Initialize minimum path
global_minimum_path: Path = min(population, key=lambda path: path.get_path_distance())
gm = []
for i in range(MAX_ITERATION):
    gm.append(global_minimum_path.get_path_distance())
    new_population = genetic_algorithm(population, num_cities)

    minimum_in_population:Path = min(new_population, key=lambda path: path.get_path_distance())

    if global_minimum_path.get_path_distance() > minimum_in_population.get_path_distance():
        global_minimum_path = minimum_in_population

    # Next Generation
    population = new_population

with open ('output.txt', 'w') as output_file:
    for city in global_minimum_path.city_list:
        output_file.write(city.get_coordination() + '\n')

    output_file.write(global_minimum_path.city_list[0].get_coordination())
