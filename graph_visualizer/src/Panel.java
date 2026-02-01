package graph_viz;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

public class Panel extends JPanel {
    private static final long serialVersionUID = 1L;
    Graph noktalar;
    
    JLabel label = new JLabel("Mouse bilgisi burada görünecek");
    
    Node selectedNode = null; // sürüklenen node
    
    Panel(Graph graf) {
        noktalar = graf;
        
        addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                int mx = e.getX();
                int my = e.getY();

                selectedNode = null;
                for (Node node : noktalar.adj) {
                    if (node.isNodeClicked(mx, my)) {
                        selectedNode = node;
                        label.setText("Node tıklandı!");
                        break;
                    }
                }

                if (selectedNode == null) {
                    label.setText("Basıldı -> X: " + mx + ", Y: " + my);
                }
            }

            @Override
            public void mouseReleased(MouseEvent e) {
                selectedNode = null;
                label.setText("Bırakıldı -> X: " + e.getX() + ", Y: " + e.getY());
            }

            @Override
            public void mouseClicked(MouseEvent e) {
                label.setText("Tıklandı -> X: " + e.getX() + ", Y: " + e.getY());
            }
        });

        addMouseMotionListener(new MouseMotionAdapter() {
            @Override
            public void mouseDragged(MouseEvent e) {
                if (selectedNode != null) {
                    selectedNode.setPos(e.getX(), e.getY());
                    repaint();
                    label.setText("Node sürükleniyor -> X: " + e.getX() + ", Y: " + e.getY());
                }
            }
        });
        
        // Başlangıç pozisyonları
        int length = 300;
        int deltax = 360 / noktalar.size();
        for (int i = 0; i < noktalar.size(); i++) {
            double radyan = Math.toRadians(i * deltax);

            int x2 = 500 + (int) (length * Math.cos(radyan));
            int y2 = 500 - (int) (length * Math.sin(radyan)); 
            noktalar.adj.get(i).setPos(x2, y2);
        }
        add(label);
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setStroke(new BasicStroke(2));

        for (int i = 0; i < noktalar.size(); i++) {
            Node node = noktalar.adj.get(i);
            for (int j : node.getConnections()) {
                Node neighbor = noktalar.adj.get(j);
                g2.drawLine(node.x, node.y, neighbor.x, neighbor.y);
            }
        }

        // Node'ları çiz
        for (int i = 0; i < noktalar.size(); i++) {
            Node node = noktalar.adj.get(i);
            int x = node.x - node.radius;
            int y = node.y - node.radius;

            g2.setColor(Color.BLUE);
            g2.fillOval(x, y, node.radius * 2, node.radius * 2);

            g2.setColor(Color.BLACK);
            g2.drawOval(x, y, node.radius * 2, node.radius * 2);

            g2.setColor(Color.WHITE);
            g2.drawString(String.valueOf(i), node.x - 5, node.y + 5);
        }
    }
}
