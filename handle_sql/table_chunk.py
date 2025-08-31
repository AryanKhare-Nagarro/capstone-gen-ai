from collections import defaultdict

def table_chunks(table_info):
    graph = defaultdict(set)
        
    for table, schema in table_info.items():
        lines = schema.splitlines()
            
        for line in lines:
            if '->' in line:
                src, target = line.strip('- ').split(" -> ")
                src_table = src.split('.')[0].strip()
                target_table = target.split('.')[0].strip()
                
                graph[src_table].add(target_table)
                graph[target_table].add(src_table)

        chunks = []
        visited = set()

        def dfs(node, group):
            visited.add(node)
            group.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, group=group)
        
        for table in table_info:
            if table not in visited:
                group = []
                dfs(table, group)
                chunk_text = "\n\n".join([table_info[g] for g in group])
                chunks.append(chunk_text)
        
        SCHEMA = chunks
        return chunks