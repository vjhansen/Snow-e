def dfs(cleaned, graph, node):
    if node not in cleaned:
        cleaned.append(node)
        for neighbour in graph[node]:
            dfs(cleaned, graph, neighbour)