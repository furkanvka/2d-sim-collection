package graph_viz;

import java.util.ArrayList;

public class Graph {
	
	ArrayList<Node> adj;
	
	public Graph(int n) {
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            adj.add(new Node());
        }
    }
	
    public void addEdge(int u, int v) {
        adj.get(u).addConnection(v);
    }
    
    public void addNode() {
    	adj.add(new Node());
    }
    
    public int size() {
    	return adj.size();
    }
}
