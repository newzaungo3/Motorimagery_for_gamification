using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum SIDE {Left,Mid,Right}
public class CarMover : MonoBehaviour
{
    public SIDE m_Side = SIDE.Mid;
    float NewXPos = -1.54f;
    public bool SwipeLeft;
    public bool SwipeRight;
    public float XValue;
    public GameObject car;
    void Start()
    {   
          
        car.transform.position = new Vector3(-1.54f,-0.49f,0);
    }

    // Update is called once per frame
    void Update()
    {
        SwipeLeft = Input.GetKeyDown(KeyCode.A) || Input.GetKeyDown(KeyCode.LeftArrow);
        SwipeRight = Input.GetKeyDown(KeyCode.D) || Input.GetKeyDown(KeyCode.RightArrow);

        if(SwipeLeft)
        {
            if(m_Side == SIDE.Mid)
            {
                NewXPos = car.transform.position.x-XValue;
                m_Side = SIDE.Left;
            }
            else if(m_Side == SIDE.Right)
            {
                NewXPos = -1.54f;
                m_Side = SIDE.Mid;
            }
        }
        else if(SwipeRight){

            if(m_Side == SIDE.Mid)
            {
                NewXPos = car.transform.position.x + XValue;
                m_Side = SIDE.Right;
            }
            else if(m_Side == SIDE.Left)
            {
                NewXPos = -1.54f;
                m_Side = SIDE.Mid;
            }
        }
        car.transform.position = new Vector3(NewXPos,-0.49f,0);
    
    }
}
