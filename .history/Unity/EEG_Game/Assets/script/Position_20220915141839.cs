using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Position : MonoBehaviour
{
    public string currentPos = "0";
    // Start is called before the first frame update
    public void setPos(string position)
    {
        Position.currentPos = position;
    }

    public string getPos()
    {
        return Position.currentPos;
    }
}
