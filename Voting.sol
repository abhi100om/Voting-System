// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    address public admin;

    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    mapping(address => bool) public registeredVoters;
    mapping(address => bool) public hasVoted;
    mapping(uint => Candidate) public candidates;
    uint public candidatesCount;
    bool public electionActive;

    constructor() {
        admin = msg.sender;
    }

    function addCandidate(string memory _name) public {
        require(msg.sender == admin, "Only admin can add candidates");
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
    }

    function registerVoter(address _voter) public {
        require(msg.sender == admin, "Only admin can register voters");
        registeredVoters[_voter] = true;
    }

    function vote(uint _candidateId) public {
        require(electionActive, "Election not active");
        require(registeredVoters[msg.sender], "You are not registered");
        require(!hasVoted[msg.sender], "You have already voted");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate");

        candidates[_candidateId].voteCount++;
        hasVoted[msg.sender] = true;
    }

    function startElection() public {
        require(msg.sender == admin, "Only admin can start");
        electionActive = true;
    }

    function endElection() public {
        require(msg.sender == admin, "Only admin can end");
        electionActive = false;
    }
}
