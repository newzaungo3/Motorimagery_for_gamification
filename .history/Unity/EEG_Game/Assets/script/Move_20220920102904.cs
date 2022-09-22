using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;

public class Move : MonoBehaviour
{
    public enum SIDE {Left,Mid,Right}
    // Start is called before the first frame update
    static string decision = "";
    public SIDE m_Side = SIDE.Mid;
    float newXPos = 0.0f;
    GameObject player;
    Vector3 pos = new Vector3(-1.54f,-0.49f,0);
    Vector3 startPos = new Vector3(-1.54f,-0.49f,0);
    void Start()
    {
        player = GameObject.FindWithTag("Player");
        player.transform.position = startPos;
        newXPos = player.transform.position.x;
        Debug.Log(newXPos);
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
        Vector3 moveVec = new Vector3(0,0,0);
        decision = Position.getPos();

        if (decision == "left")
        {   if(m_side == SIDE.Mid)
            {
                moveVec = new Vector3(-4.14f,-0.49f,0);
            }
        }
        else if (decision == "right")
        {
            moveVec = new Vector3(1.19f,-0.49f,0);
        }
        else{
            moveVec = new Vector3(-1.54f,-0.49f,0);
        }
        return moveVec;
    }

    
}
