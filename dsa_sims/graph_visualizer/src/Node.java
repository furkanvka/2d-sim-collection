package graph_viz;

import java.util.ArrayList;

public class Node {

    private ArrayList<Integer> connection;
    int x;
    int y;

    int radius = 20;

    public Node() {
        connection = new ArrayList<>();
    }

    public void addConnection(int a) {
        connection.add(a);
    }

    public boolean isConnect(int a) {
        return connection.contains(a);
    }
    
    
    public void setPos(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public ArrayList<Integer> getConnections() {
        return connection;
    }
    
    
    boolean isNodeClicked(int mouseX, int mouseY) {
        int dx = mouseX - this.x;
        int dy = mouseY - this.y;
        return dx * dx + dy * dy <= radius * radius;
    }

}
