import random
from deap import creator, base, tools, algorithms
from ka_operator import Conv
from mem import Fram

fram = Fram()
conv1 = Conv(
    "onnx",
    [1, 3, 384, 704],
    [1, 64, 192, 352],
    [7, 7],
    [3, 3, 3, 3],
    [2, 2],
)
conv1.onnx_to_ka(fram.bank_width)
input = conv1.inp
output = conv1.outp
weight = conv1.weight

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()


def ind_generator(input, outp):
    Cin = random.randint(1, input[1])
    Cout = random.randint(1, output[1])
    Ho = random.randint(1, output[2])
    Wo = random.randint(1, output[3])
    return [Cin, Cout, Ho, Wo]


toolbox.register("attr_params", ind_generator, input, output)
# toolbox.register("attr_inp_c", random.randint, 1, input[1])
# toolbox.register("attr_outp_c", random.randint, 1, output[1])
# toolbox.register("attr_height_c", random.randint, 1, output[2])
# toolbox.register("attr_width_c", random.randint, 1, output[3])

# toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register(
    "individual",
    tools.initRepeat,
    creator.Individual,
    toolbox.attr_params,
    n=100,
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def evalOneMax(individual):
    return (sum(individual),)


toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

population = toolbox.population(n=100)

NGEN = 40
for gen in range(NGEN):
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
    fits = toolbox.map(toolbox.evaluate, offspring)
    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
    population = toolbox.select(offspring, k=len(population))
top10 = tools.selBest(population, k=10)
