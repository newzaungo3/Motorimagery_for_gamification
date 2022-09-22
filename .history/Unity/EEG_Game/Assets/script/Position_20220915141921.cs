using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Position : MonoBehaviour
{
    static string currentPos = "0"
    // Start is called before the first frame update
    public static void setPos(string position)
    {
        Position.currentPos = position;
    }

    public static string getPos()
    {
        return Position.currentPos;
    }
}
