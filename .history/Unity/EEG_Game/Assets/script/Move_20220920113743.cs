using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;

public class Move : MonoBehaviour
{
    public enum SIDE {Left,Mid,Right}

    static SIDE m_Side = SIDE.Mid;
    // Start is called before the first frame update
    static string decision = "";
    static GameObject player;
    Vector3 pos = new Vector3(-1.54f,-0.49f,0);
    Vector3 startPos = new Vector3(-1.54f,-0.49f,0);
    void Start()
    {
        player = GameObject.FindWithTag("Player");
        player.transform.position = startPos;
    }

    // Update is called once per frame
    void Update()
    {
        //Debug.Log("Position "+  Position.getPos());
        pos = moveBall();
        player.transform.position = pos;
    }

    void Run()
    {
        Debug.Log("lastvector" + pos);
        pos = moveBall();
    }

    public static Vector3 moveBall()
    {   
        player = GameObject.FindWithTag("Player");
        string decision = "";
        float newXPos = -1.54f;
        float xValue = 2.6f;

        Vector3 moveVec = new Vector3(-1.54f,-0.49f,0);
        decision = Position.getPos();

        if (decision == "left") 
        {   
            if(m_Side == SIDE.Mid)
            {   
                Debug.Log("Hello world");
                newXPos = player.transform.position.x - xValue;
                Debug.Log(newXPos); 
                //moveVec = new Vector3(-4.14f,-0.49f,0.0f);
                m_Side = SIDE.Left;
                Position.setPos("");
            }    
            else if(m_Side == SIDE.Right)
            {
                newXPos = -1.54f; 
                //moveVec = new Vector3(-1.54f,-0.49f,0);
                m_Side = SIDE.Mid;
                Position.setPos("");
            }

        }
        else if (decision == "right")
        {   
            if(m_Side == SIDE.Mid)
            {   
                newXPos = player.transform.position.x + xValue; 
                //moveVec = new Vector3(1.19f,-0.49f,0);
                m_Side = SIDE.Right;
                Position.setPos("");
            }    
            else if(m_Side == SIDE.Left)
            {
                newXPos = -1.54f;
                //moveVec = new Vector3(-1.54f,-0.49f,0);
                m_Side = SIDE.Mid;
                Position.setPos("");
            }
        }
        //send finish vector (calculate version)
        moveVec = new Vector3(newXPos,-0.49f,0);
        Debug.Log(moveVec);
        return moveVec;
    }

    
}