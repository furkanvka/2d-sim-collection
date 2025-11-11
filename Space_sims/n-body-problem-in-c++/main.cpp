#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <cmath>


#define G 6.674E-11 // m3/(kg·s2)
#define PIXEL_KM 20000.0f
#define TRAIL_DROP_RATE 0.05f
#define SİM_SPEDD 100.f

class Body : public sf::CircleShape
{
public:
    double mass;
    sf::Vector2f velocity;
    sf::Vector2f acceleration;
    bool trail;


    std::vector<sf::CircleShape> trailPoints;
    sf::Clock trailClock; 
    const size_t maxTrailLength = 200; 


    Body(float x, float y, float r, double m, sf::Color color, bool t);


    void updateTrail();
    void updatePos(float dt);
};

Body::Body(float x, float y, float r, double m, sf::Color color, bool t) : mass(m), trail(t)
{
    setRadius(r);
    setOrigin(r, r); 
    setFillColor(color);
    setPosition(x, y);
    velocity = sf::Vector2f(0.f, 0.f);
    acceleration = sf::Vector2f(0.f, 0.f);
}

void Body::updatePos(float dt) {
    velocity += acceleration * dt;
    sf::Vector2f movement = (velocity / PIXEL_KM )* dt;
    move(movement);
    
    updateTrail();
}

void Body::updateTrail() {
    if (!trail) return; 

    if (trailClock.getElapsedTime().asSeconds() >= TRAIL_DROP_RATE) {
        
        sf::CircleShape point(1.f); 
        point.setPosition(getPosition());
        
        sf::Color trailColor = getFillColor();
        trailColor.a = 150;
        point.setFillColor(trailColor);

        trailPoints.push_back(point);

        // Maksimum uzunluğu aşarsa en eski noktayı sil
        if (trailPoints.size() > maxTrailLength) {
            trailPoints.erase(trailPoints.begin());
        }

        trailClock.restart();
    }
}

// --- Gravity Calculation Function ---
void calculateGravityEffects(std::vector<Body>& bodies) {
    
    for (auto& body : bodies) {
        body.acceleration = sf::Vector2f(0.f, 0.f);
    }


    for (int i = 0; i < bodies.size(); i++) {
        for (int j = i + 1; j < bodies.size(); j++) {
            Body& body1 = bodies[i];
            Body& body2 = bodies[j];

            sf::Vector2f direction = body2.getPosition() - body1.getPosition();
            
            float r_sq = direction.x * direction.x + direction.y * direction.y;
            float r = std::sqrt(r_sq);
            
            if (r_sq < 1.0f) { 
                continue; 
            }
            
            float r_km = r * PIXEL_KM;
            float r_sq_km = r_km * r_km;
            
            float acc_mag_1 = (float)(G * body2.mass / r_sq_km);
            
            float acc_mag_2 = (float)(G * body1.mass / r_sq_km);
            
            // 4. Calculate the unit vector (r_hat)
            sf::Vector2f unit_direction = direction / r;

            body1.acceleration += acc_mag_1 * unit_direction;
            
            body2.acceleration += acc_mag_2 * -unit_direction;
        }
    }
}


// --- Main Function ---
int main()
{
    const int WIDTH = 1920;
    const int HEIGHT = 1080;
    sf::RenderWindow window(sf::VideoMode(WIDTH, HEIGHT), "N Body Problem");

    sf::Clock clock;

    std::vector<Body> bodies;

    bodies.emplace_back(WIDTH/2, HEIGHT/2, 25.f, 5e24, sf::Color::Yellow,false);

    bodies.emplace_back(WIDTH/2 + 150.f, HEIGHT/2, 10.f, 5e15, sf::Color::Green,true);
    bodies.back().velocity = sf::Vector2f(0.f, +10000.0f); 

    bodies.emplace_back(WIDTH/2 - 200.f, HEIGHT/2, 16.f, 5e23, sf::Color::Blue,true);
    bodies.back().velocity = sf::Vector2f(0.f, -9000.0f); 


    while (window.isOpen())
    {
        sf::Event e;
        while (window.pollEvent(e))
        {
            if (e.type == sf::Event::Closed) window.close();
        }
        
        float dt = clock.restart().asSeconds();
        dt *= SİM_SPEDD;
        
        calculateGravityEffects(bodies);

        window.clear(sf::Color::Black);
        for (auto& body : bodies) {
            body.updatePos(dt);
        }
        for (const auto& body : bodies) {
            if (body.trail) {
                for (const auto& point : body.trailPoints) {
                    window.draw(point);
                }
            }
        }


        for (const auto& body : bodies) {
            window.draw(body);
        }


        
        
        window.display();
    }

    return 0;
}