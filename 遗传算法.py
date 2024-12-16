import random
import tkinter
from functools import reduce

#设置随机种子
random.seed(123)

# 参数设置
city_num = 50  # 城市数量
population_size = 100  # 种群大小
generations = 100  # 最大迭代次数
mutation_rate = 0.2  # 变异率

# 随机生成城市的坐标
distance_x = [random.randint(50, 750) for _ in range(city_num)]
distance_y = [random.randint(50, 550) for _ in range(city_num)]

# 计算城市之间的距离
distance_graph = [[0.0 for _ in range(city_num)] for _ in range(city_num)]
for i in range(city_num):
    for j in range(city_num):
        distance_graph[i][j] = ((distance_x[i] - distance_x[j]) ** 2 + (distance_y[i] - distance_y[j]) ** 2) ** 0.5

# 路径距离计算函数
def calculate_distance(path):
    return sum(distance_graph[path[i]][path[i + 1]] for i in range(-1, city_num - 1))

# 2-Opt 局部搜索优化
def two_opt(path):
    best_path = path[:]
    best_distance = calculate_distance(path)
    for i in range(1, len(path) - 1):
        for j in range(i + 1, len(path)):
            new_path = path[:]
            new_path[i:j] = reversed(new_path[i:j])
            new_distance = calculate_distance(new_path)
            if new_distance < best_distance:
                best_path, best_distance = new_path, new_distance
    return best_path

# 遗传算法类
class GeneticAlgorithm:
    def __init__(self):
        self.best_path = None
        self.best_distance = float('inf')

    def init_population(self):
        """ 初始化种群：随机生成路径 """
        return [random.sample(range(city_num), city_num) for _ in range(population_size)]

    def crossover(self, parent1, parent2):
        """ 有序交叉（Order Crossover, OX） """
        cut1, cut2 = sorted(random.sample(range(city_num), 2))
        child = [-1] * city_num
        child[cut1:cut2] = parent1[cut1:cut2]
        pointer = cut2
        for city in parent2:
            if city not in child:
                child[pointer % city_num] = city
                pointer += 1
        return child

    def mutate(self, path):
        """ 变异操作：交换两个城市的位置 """
        if random.random() < mutation_rate:
            i, j = random.sample(range(city_num), 2)
            path[i], path[j] = path[j], path[i]

    def run(self, canvas, draw_path, root):
        """ 遗传算法主循环，实时可视化路径 """
        population = self.init_population()
        for gen in range(generations):
            # 选择和排序
            population = sorted(population, key=calculate_distance)
            new_population = population[:10]  # 精英保留

            # 交叉和变异生成新种群
            while len(new_population) < population_size:
                p1, p2 = random.choices(population[:30], k=2)
                child = self.crossover(p1, p2)
                self.mutate(child)
                new_population.append(two_opt(child))  # 局部优化

            # 更新最优解
            population = new_population
            current_best = min(population, key=calculate_distance)
            current_distance = calculate_distance(current_best)
            if current_distance < self.best_distance:
                self.best_distance = current_distance
                self.best_path = current_best

            # 可视化当前最优路径
            draw_path(self.best_path)
            root.update()

            print(f"Generation {gen + 1}, Best Distance: {self.best_distance}")

        return self.best_path, self.best_distance

# 可视化类
class TSPVisualizer:
    def __init__(self, root):
        self.root = root
        self.canvas = tkinter.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()
        self.nodes = [(distance_x[i], distance_y[i]) for i in range(city_num)]
        self.ga = GeneticAlgorithm()
        self.draw_nodes()

    def draw_nodes(self):
        """ 绘制城市节点 """
        for x, y in self.nodes:
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")

    def draw_path(self, path):
        """ 绘制路径 """
        self.canvas.delete("path")
        for i in range(-1, city_num - 1):
            x1, y1 = self.nodes[path[i]]
            x2, y2 = self.nodes[path[i + 1]]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", tags="path")

    def run(self):
        """ 运行遗传算法并可视化路径 """
        best_path, best_distance = self.ga.run(self.canvas, self.draw_path, self.root)
        self.draw_path(best_path)
        print("Final Best Path:", best_path)
        print("Final Best Distance:", best_distance)

# 主函数
if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Genetic Algorithm for TSP")
    tsp = TSPVisualizer(root)
    tsp.run()
    root.mainloop()
