using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;
using UnityEngine.SceneManagement;
public class Move : MonoBehaviour
{
    public enum SIDE {Left,Mid,Right}

    static SIDE m_Side = SIDE.Mid;
    // Start is called before the first frame update
    static string decision = "";
    static GameObject player;
    Vector3 pos = new Vector3(-1.54f,-0.49f,0);
    Vector3 startPos = new Vector3(-1.54f,-0.49f,0);

    static Vector3 moveVec = new Vector3(-1.54f,-0.49f,0);

    static float newXPos = -1.54f;
    static float xValue = 2.6f;

    static float timeRemaining = 5;


    void Start()
    {
        player = GameObject.FindWithTag("Player");
        player.transform.position = startPos;

        // Toggle fullscreen
        //Screen.fullScreen = !Screen.fullScreen;
    }

    // Update is called once per frame
    void Update()
    {
        //Debug.Log("Position "+  Position.getPos());
        pos = moveBall();
        player.transform.position = pos;

        if (pos =! startPos)
        {

        }

        if(Input.GetKeyDown(KeyCode.Escape) == true)
        {
            Application.Quit();
        }
        if(Input.GetKeyDown(KeyCode.Backspace) == true)
        {
            SceneManager.LoadScene(0);
        }
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
        decision = Position.getPos();

        if (decision == "left") 
        {   
            if(m_Side == SIDE.Mid)
            {   
                newXPos = player.transform.position.x - xValue;
                Debug.Log(newXPos); 
                m_Side = SIDE.Left;
                Position.setPos("");
            }    
            else if(m_Side == SIDE.Right)
            {
                newXPos = -1.54f; 
                m_Side = SIDE.Mid;
                Position.setPos("");
            }

        }
        else if (decision == "right")
        {   
            if(m_Side == SIDE.Mid)
            {   
                newXPos = player.transform.position.x + xValue; 
                m_Side = SIDE.Right;
                Position.setPos("");
            }    
            else if(m_Side == SIDE.Left)
            {
                newXPos = -1.54f;
                m_Side = SIDE.Mid;
                Position.setPos("");
            }
        }
        //send finish vector (calculate version)
        moveVec = new Vector3(newXPos,-0.49f,0);;
        return moveVec;
    }

    public static Vector3 reset()
    {   
        float timeRamaining = 5.0; 
        if (timeRemaining > 0)
        {
            timeRemaining -= Time.deltaTime;
        }
        else
        {
            moveVec = new Vector3(-1.54,-0.49f,0);;
        }
    }

    
}
