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
    }

    // Update is called once per frame
    void Update()
    {
        Debug.Log("Position "+  Position.getPos());
    }
}
