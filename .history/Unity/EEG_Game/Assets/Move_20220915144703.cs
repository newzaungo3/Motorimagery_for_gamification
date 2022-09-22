using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;

public class Move : MonoBehaviour
{
    // Start is called before the first frame update
    string pos = "";
    void Start()
    {
        pos = Position.getPos();
        Debug.Log("ESUS" + pos);
        // Debug.Log("Position "+ Position.currentPos);
        
    }

    // Update is called once per frame
    void Update()
    {
        Debug.Log("Position "+ sendPosition.currentPos);
    }
}
