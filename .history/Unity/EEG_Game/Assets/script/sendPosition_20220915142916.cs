using System;
using System.Collections;
using System.Threading;
using System.Collections.Generic;
using UnityEngine;

public class sendPosition : MonoBehaviour
{   
    bool running;
    GameObject cube;
    static string currentPos = "0";
    Vector3 pos = new Vector3(-1.54f,-0.49f,0);
    Vector3 startPos = new Vector3(-1.54f,-0.49f,0);
    // Start is called before the first frame update
    void Start()
    {
        cube = GameObject.FindWithTag("Player");
        cube.transform.position = startPos;
        running = true;
    }

    // Update is called once per frame
    void Update()
    {   
        Debug.Log("Position "+ sendPosition.currentPos);
        pos = moveBall();
        cube.transform.position = pos;
    }
    void Run()
    {
        Debug.Log("lastvector" + pos);
        pos = moveBall();
    }

    public static Vector3 moveBall()
    {   
        string dec = "";
        string decision = "";
        Vector3 moveVec = new Vector3(0,0,0);
        decision = sendPosition.currentPos;
        if (decision == "left")
        {
            moveVec = new Vector3(-5,-0.49f,0);
        }
        else if (decision == "right")
        {
            moveVec = new Vector3(5,-0.49f,0);
        }
        else{
            moveVec = new Vector3(-1.54f,-0.49f,0);
        }
        return moveVec;
    }

    public static void setPos(string position)
    {
        sendPosition.currentPos = position;
    }

    public static string getPos()
    {
        return sendPosition.currentPos;
    }

}
