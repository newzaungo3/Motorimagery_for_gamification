using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;

public class Move : MonoBehaviour
{
    // Start is called before the first frame update
    static string pos = "";
    void Start()
    {
        pos = Position.getPos();
        Debug.Log("Position "+ Position.currentPos);
        if(pos == "left")
        {
            Debug.Log(pos);
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
