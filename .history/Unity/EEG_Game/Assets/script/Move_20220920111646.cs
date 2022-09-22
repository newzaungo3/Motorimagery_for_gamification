using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;

public class Move : MonoBehaviour
{
    public enum SIDE {Left,Mid,Right}
    // Start is called before the first frame update
    static string decision = "";
    GameObject player;
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
        
        string decision = "";
        float newXPos = 0.0f;
        float xValue = 2.6f;

        Vector3 moveVec = new Vector3(-1.54f,-0.49f,0);
        decision = Position.getPos();

        SIDE m_Side = SIDE.Mid;

        if (decision == "left") 
        {   
            if(m_Side == SIDE.Mid)
            {   
                moveVec = new Vector3(-4.14f,-0.49f,0.0f);
                m_Side = SIDE.Left;

            }    
            else if(m_Side == SIDE.Right)
            {
                moveVec = new Vector3(-1.54f,-0.49f,0);
                m_Side = SIDE.Mid;
            }

        }
        else if (decision == "right")
        {   
            if(m_Side == SIDE.Mid)
            {   
                moveVec = new Vector3(1.19f,-0.49f,0);
                m_Side = SIDE.Right;
            }    
            else if(m_Side == SIDE.Left)
            {
                moveVec = new Vector3(-1.54f,-0.49f,0);
                m_Side = SIDE.Mid;
            }
        }
        else{
            moveVec = new Vector3(-1.54f,-0.49f,0);
        }
        return moveVec;
    }

    
}
