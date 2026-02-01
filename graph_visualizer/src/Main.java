package graph_viz;

import javax.swing.*;

public class Main {
    public static void main(String[] args) {
    	Graph graf = new Graph(5);
    	graf.addEdge(1, 2);
    	graf.addEdge(0, 2);
    	graf.addEdge(4, 3);
    	graf.addEdge(2, 3);
    	
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Simple Line and Points");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(1000, 1000);
            frame.setLocationRelativeTo(null);

            Panel panel = new Panel(graf);
            frame.add(panel);

            frame.setVisible(true);
        });
    }
}
